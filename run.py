from juno import *

from os.path import join, exists
import subprocess
import datetime;
import threading;
import os
import sys

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
  
def exec_ci_cmd(cmd):
  """execute a comand inside .ci folder and return result"""
  if exists(join(repo_path, CIPY_FOLDER, cmd)):
    build_cmd = join(".", CIPY_FOLDER, cmd);
    return cmd([build_cmd], repo_path);
  return (None, None)
    
  
@route('/build')
def build(web):
  b = Build(date=datetime.datetime.now().strftime("%b%d %H:%M"), finished=False)
  b.save();
  # i was using a thread before but sqlite doesn't support access to same object from different threads
  pid = os.fork();
  if pid == 0:
    cmd(update_cmds[repo_type], repo_path);
    data, ret = dataexec_ci_cmd("build");
    if ret != None:
      b.result = ret;
      b.output = data.replace("\n", "<br />");
    else:
      b.output = "%s file not found, i don't know how to build" % join(CIPY_FOLDER, "build");
    b.finished = True;
    b.save();

    # hooks
    if ret == 0:
      exec_ci_cmd("build_pass");
    else:
      exec_ci_cmd("build_failed");
    sys.exit()
  else:
    return "scheduled!"
 

@route('/')
def index(web):
  builds = find(Build).order_by(Build.id.desc()).all();
  template("index.html", { 'builds': builds, 'project_path': repo_path })
  

if __name__ == '__main__':
  if len(sys.argv) == 2:
    repo_path = sys.argv[1];
    repo_type = get_repo_type(repo_path);
    if repo_type:
      print "repository type: %s" % repo_type
      run()
    else:
      print "unknow repository type"


