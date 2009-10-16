from juno import *

from os.path import join, exists
import subprocess
import datetime;

repo_path = '/home/javi/tmp/test_repo'
#init juno
init({'db_location': 'cipy.db'})

Build = model('Build', date='str', result='int', output='str')

def cmd(l, cwd = None):
  """ execute a system command """
  p = subprocess.Popen(" ".join(l), cwd=cwd, shell=True, bufsize=2048, stdout=subprocess.PIPE, stderr=subprocess.STDOUT);
  data = p.stdout.read()
  retcode = p.wait()
  return (data, retcode)

@route('/build')
def build(web):
  cmd(["git", "reset", "--hard"], repo_path);
  build = join(repo_path,"ci","build");
  if exists(build):
    data, ret = cmd(["/bin/sh", build], repo_path);
  else:
    data = "ci/build doesn't exist"
  Build(date=datetime.datetime.now().ctime(), result=ret, output=data).save();

  return data;

@route('/')
def index(web):
  builds = find(Build).all();
  template("index.html", { 'builds': builds })
  

if __name__ == '__main__':
  if len(sys.argv) == 2:
    repo_path = sys.argv[1];
    run()


