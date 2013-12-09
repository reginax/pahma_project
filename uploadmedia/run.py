import os
import sys

env =  {"PATH": os.environ["PATH"] + ":/usr/local/share/django/pahma_project/uploadmedia" }
print "argument "+sys.argv[1]
os.execlpe("bulkmediaupload.sh", "",sys.argv[1], env)
