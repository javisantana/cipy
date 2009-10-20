from juno import *

from os.path import join, exists
import subprocess
import datetime;
import threading;
import os
import sys
import urllib;

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

scm_cmds = { 'git': {'reset':["git", "reset", "--hard"], 
                     'rev':["git", "rev-parse", "HEAD"]},
                'svn': {'reset':["svn", "update"], 
                        'rev':["svnversion"] }
              };

#init juno
init({'db_location': 'cipy.db', 'dev_port':8000})

Build = model('Build', date='str', result='int', output='str', finished='boolean', rev='str');

def cmd(l, cwd = None):
  """ execute a system command """
  print "executing: ", " ".join(l)
  p = subprocess.Popen(" ".join(l), cwd=cwd, shell=True, bufsize=2048, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
  data = p.stdout.read().decode('utf-8')
  retcode = p.wait()
  return (data, retcode)
  
def exec_ci_cmd(c):
  """execute a comand inside .ci folder and return result"""
  if exists(join(repo_path, CIPY_FOLDER, c)):
    build_cmd = join(".", CIPY_FOLDER, c);
    return cmd([build_cmd], repo_path);
  return (None, None)
  
def build_work(build_id):
    cmd(scm_cmds[repo_type]['reset'], repo_path);
    data, ret = exec_ci_cmd("build");
    if ret != None:
      data = data.replace("\n", "<br />");
    else:
      data = "%s file not found, i don't know how to build" % join(CIPY_FOLDER, "build");

    # make a post to localhost
    # using this trick cipy avoids sqlite problems with threads
    #TODO: change port!
    params = urllib.urlencode({'id': build_id,  'output': data, 'ret': ret})
    urllib.urlopen("http://127.0.0.1:8000/finish", params).read();

    # hooks
    if ret == 0:
      exec_ci_cmd("build_pass");
    else:
      exec_ci_cmd("build_failed");

@route('/finish')
def build_finished(web):
    b = find(Build).filter(Build.id == web.input()['id']).one()
    b.finished = True;
    b.output = web.input()['output'];
    b.result = web.input()['ret'];
    b.save();
    return "ok";

@route('/build')
def build(web):
  #get revision
  data, ret = cmd(scm_cmds[repo_type]['rev'], repo_path);
  b = Build(date=datetime.datetime.now().strftime("%b%d %H:%M"), finished=False, rev=data[:6])
  b.save();

  # launch build thread
  threading.Thread(target=build_work, args=(b.id,)).start();
  return "scheduled!"
 

@route('/')
def index(web):
  builds = find(Build).order_by(Build.id.desc()).limit(10).all();
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


