cipy
====

A *really* small quick'n'dirty continuous integration written in python.

cipy is language independent, it only execute a command and checks the return value , 0 = PASS, FAIL otherwise.

cipy uses the same aproach than git, svn and other SCM, use a special folder called .ci where the commands that will be executed to build are stored.

Installation
------------

For the moment, cipy only runs on Linux (and maybe on macos and other unix flavours) and you need to install the following requirements:
    $ python >= 2.5
    $ juno (mini web framework)
    $ SQLAlchemy (for models)
    $ jinja2 (html template library)

juno, SQLAlchemy and jinja2 can be installed through pip

Usage
-----

cipy doesn't need installation, only clone this repository and run!:
    $ git clone git://github.com/javisantana/cipy.git
    $ cd cipy
    $ python run.py /path/to/repo
  
repo must be owned by cipy because it performs reset/update and you could loss your work if you're working in the same copy.
once cipy has started you can open your favorite browser and point it to http://localhost:8000

.ci folder must exists in the repo root and a file called `build` (inside it) with execution permissions.This is the file that will be called in each build.

to raise a build use wget or other http client to call http://host:8000/build. You can put this statement inside post-commit-hook in svn or inside post-recieve-hook in git:
    $ wget http://host:8000/build -O/dev/null

You also can trigger a build by hand using the web interface.

you can see a [screenshot](http://web2.twitpic.com/m9kjj) (if you're a real man)

TODO
----
    [ ] add cmd line configuration parameters
    [ ] support more than a repository
    [ ] windows version 
    [ ] improve my written english skills


javisantana, qualopec (a) gmail.com | @javisantana






