from juno import *

from os.path import join, exists
import subprocess
import datetime;
import threading;
import os
import sys
from Queue import Queue

CIPY_FOLDER = ".ci"

repo_path = None
repo_type = None

finished_jobs = Queue();

def save_pending_jobs():
 while not finished_jobs.empty():
     w = finished_jobs.get()
     w.save();
     finished_jobs.task_done()

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
init({'db_location': 'cipy.db'})

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
  
def build_work(b):
    cmd(scm_cmds[repo_type]['reset'], repo_path);
    data, ret = exec_ci_cmd("build");
    if ret != None:
      b.result = ret;
      b.output = data.replace("\n", "<br />");
    else:
      b.output = "%s file not found, i don't know how to build" % join(CIPY_FOLDER, "build");
    b.finished = True;
    finished_jobs.put(b)
    # hooks
    if ret == 0:
      exec_ci_cmd("build_pass");
    else:
      exec_ci_cmd("build_failed");
  
  
@route('/build')
def build(web):
  save_pending_jobs();

  #get revision
  data, ret = cmd(scm_cmds[repo_type]['rev'], repo_path);
  b = Build(date=datetime.datetime.now().strftime("%b%d %H:%M"), finished=False, rev=data[:6])
  b.save();

  # launch build thread
  threading.Thread(target=build_work, args=(b,)).start();
  return "scheduled!"
 

@route('/')
def index(web):
  save_pending_jobs();
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


