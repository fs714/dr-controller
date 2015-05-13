import logging
import logging.config
from webob import Request


def url_recorder_factory(global_conf, **local_conf):
    def filter(app):
        return UrlRecorder(app, global_conf, local_conf)
    return filter


class UrlRecorder(object):
    def __init__(self, app, global_conf, local_conf):
        logging.config.fileConfig("./etc/logging.conf")
        self.logger = logging.getLogger("record_url")
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)

        url = req.url
        self.logger.info("--------------------------------")
        self.logger.info(url)
        self.logger.info("------")

        for name, value in sorted(req.environ.items()):
            self.logger.info(name + " = " + str(value))

        return self.app(environ, start_response)
