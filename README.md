#ftpython

ftpython is a simple ftp client for your command line, written in python. It is a work in progress, but supported commands will be kept track of in this file.

##Setup

ftpython uses the setuptools package for installation. If you don't have it, you can install it by running:

`pip install setuptools`

To setup ftpython, navigate to the cloned directory and run:

`python setup.py install`

##Use
To start ftpython, run:

`python -m ftpython`

You will then see this prompt for command:

`ftpython>`

The following commands are supported:
- ascii
- cat
- cd
- cdup
- close
- delete
- get
- help
- image
- lcd
- lds (Accepts an optional '-l' flag, calls an 'ls' command on the local working directory)
- ls
- mdelete
- mget
- mkdir
- mput
- prompt
- put
- pwd
- rename
- rmdir
- size
- type
- user
