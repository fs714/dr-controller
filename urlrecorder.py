import logging
import logging.config
from webob import Request, Response


class record_url:
    def __init__(self):
        logging.config.fileConfig("logging.conf")
        self.logger = logging.getLogger("record_url")

    def __call__(self, environ, start_response):
        req = Request(environ)
        res = Response()

        url = req.url
        self.logger.info("--------------------------------")
        self.logger.info(url)
        self.logger.info("------")

        res.content_type = 'text/plain'
        parts = []
        for name, value in sorted(req.environ.items()):
            parts.append('%s: %r' % (name, value))
            self.logger.info(name + " = " + str(value))
        res.body = '\n'.join(parts)
        res.body += '\n'

        return res(environ, start_response)
