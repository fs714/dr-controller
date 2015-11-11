import eventlet
import os
import sys
import logging
import logging.config
import commands
from eventlet import wsgi
from paste.deploy import loadapp
import multiprocessing
from heartbeat import heartbeat

# Monkey patch socket, time, select, threads
eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True, os=True)


def main():
    # Init logger
    root_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    log_config_path = root_path + '/conf/logging.conf'
    logging.config.fileConfig(log_config_path)
    logging.getLogger("sqlalchemy.engine.base.Engine").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)
    logger = logging.getLogger("HttpServer")
    logger.info('Http Server Start')

    # Start heartbeat for primary site
    process = multiprocessing.Process(target=heartbeat, args=())
    process.start()

    # Start drcontroller http service
    conf = "conf/api-paste.ini"
    appname = "main"
    # commands.getoutput('mkdir -p /home/eshufan/dr_log/')
    app = loadapp("config:%s" % os.path.abspath(conf), appname)
    wsgi.server(eventlet.listen(('', 80)), app)

if __name__ == '__main__':
    main()
