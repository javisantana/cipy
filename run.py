from juno import *

from os.path import join, exists
import subprocess
import datetime;
import threading;
import os

CIPY_FOLDER = ".ci"

repo_path = None
repo_type = None


def get_repo_type(path):
  """ return repo type based on configuration folder, i.e .git, .svn """
  if(exists(join(path, ".git"))):
    return "git"
  elif(exists(join(path, ".svn"))):
    return "svn";
  return None

update_cmds = { 'git': ["git", "reset", "--hard"], 
                'svn': ["svn", "update"] 
              };

#init juno
init({'db_location': 'cipy.db'})

Build = model('Build', date='str', result='int', output='str', finished='boolean');

def cmd(l, cwd = None):
  """ execute a system command """
  print "executing: ", " ".join(l)
  p = subprocess.Popen(" ".join(l), cwd=cwd, shell=True, bufsize=2048, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
  data = p.stdout.read().decode('utf-8')
  retcode = p.wait()
  return (data, retcode)
  
@route('/build')
def build(web):
  cmd(update_cmds[repo_type], repo_path);
  b = Build(date=datetime.datetime.now().strftime("%b%d %H:%M"), finished=False)
  b.save();
  # i was using a thread before but sqlite doesn't support access to same object from different threads
  pid = os.fork();
  if pid == 0:
    if exists(join(repo_path, CIPY_FOLDER, "build")):
      build_cmd = join(".", CIPY_FOLDER, "build");
      data, ret = cmd([build_cmd], repo_path);
      b.result = ret;
      b.output = data.replace("\n", "<br />");
    else:
      b.output = "%s file not found, i don't know how to build" % build_cmd
    b.finished = True;
    b.save();
    #TODO call success and fail hooks
    sys.exit()
  else:
    return "scheduled!"
 

@route('/')
def index(web):
  builds = find(Build).order_by(Build.id.desc()).all();
  template("index.html", { 'builds': builds })
  

if __name__ == '__main__':
  if len(sys.argv) == 2:
    repo_path = sys.argv[1];
    repo_type = get_repo_type(repo_path);
    if repo_type:
      print "repository type: %s" % repo_type
      run()
    else:
      print "unknow repository type"


