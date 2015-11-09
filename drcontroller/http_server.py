import eventlet
import os
import commands
from eventlet import wsgi
from paste.deploy import loadapp
import sys
import multiprocessing
from heartbeat import heartbeat

# Monkey patch socket, time, select, threads
eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True, os=True)


def main():
    # Start heartbeat for primary site
    process = multiprocessing.Process(target=heartbeat, args=())
    process.start()

    # Start drcontroller http service
    conf = "conf/api-paste.ini"
    appname = "main"
    commands.getoutput('mkdir -p ../logs')
    app = loadapp("config:%s" % os.path.abspath(conf), appname)
    wsgi.server(eventlet.listen(('', 80)), app)

if __name__ == '__main__':
    main()
