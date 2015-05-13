import eventlet
import os
from eventlet import wsgi
from paste.deploy import loadapp

conf = "etc/api-paste.ini"
appname = "main"
#import pdb
#pdb.set_trace()
app = loadapp("config:%s" % os.path.abspath(conf), appname)

wsgi.server(eventlet.listen(('', 80)), app)
