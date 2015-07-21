import json
import eventlet
from eventlet import wsgi
from webob import Request, Response


class WsgiApp(object):
    def __init__(self):
        print('WsgiApp init')

    def __call__(self, environ, start_response):
        print('WsgiApp::__call__ start')
        req = Request(environ)
        print_req_env(req)
        res = Response()
        res.content_type = 'application/json'
        res.body = json.dumps(req.json, indent=4, sort_keys=True)
        return res(environ, start_response)


class WsgiMiddle01(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle01 init')

    def __call__(self, environ, start_response):
        print('WsgiMiddle01::__call__ start')
        req = Request(environ)
        res = req.get_response(self.app)
        print('WsgiMiddle01::__call__ After call its app')
        return res(environ, start_response)


class WsgiMiddle02(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle02 init')

    def __call__(self, environ, start_response):
        print('WsgiMiddle02::__call__ start')
        req = Request(environ)
        res = req.get_response(self.app)
        print('WsgiMiddle02::__call__ After call its app')
        return res(environ, start_response)


def print_req_env(req):
    env = req.environ
    for name, value in sorted(env.items()):
        print(name + " = " + str(value))
    return env


def main():
    app = WsgiMiddle01(WsgiMiddle02(WsgiApp()))
    wsgi.server(eventlet.listen(('', 80)), app)


if __name__ == '__main__':
    main()
