import logging
import logging.config
import json
import re
from webob import Request


def url_recorder_factory(global_conf, **local_conf):
    def filter(app):
        return UrlRecorder(app, global_conf, local_conf)
    return filter


class UrlRecorder(object):
    def __init__(self, app, global_conf, local_conf):
        logging.config.fileConfig("./conf/logging.conf")
        self.logger = logging.getLogger("record_url")
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)

        if req.method == 'POST' and req.content_type == 'application/json':
            updated_env = self.print_log(req)
            environ['updated_env'] = updated_env
        else:
            start_response("200 OK", [("Content-type", "text/plain")])
            return ['Only post with json supported now!\n']

        return self.app(environ, start_response)

    def print_log(self, req):
        env = req.environ.copy()
        for name, value in sorted(env.items()):
            self.logger.debug(name + " = " + str(value))
            if name != 'HTTP_OPENSTACK_SERVICE':
                if self.has_object_address(str(value)):
                    del env[name]
        env['wsgi.input'] = req.json
        self.logger.info('--------------------------------')
        self.logger.info(json.dumps(env, indent=4, sort_keys=True))
        self.logger.info('--------------------------------')
        return env

    def has_object_address(self, value):
        pattern = re.compile(r'.*0x[0-9a-f]{12}')
        match = pattern.match(value)
        if match:
            return True
        else:
            return False
