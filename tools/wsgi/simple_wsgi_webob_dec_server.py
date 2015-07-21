import json
import webob.dec
import eventlet
from eventlet import wsgi
from webob import Response


class WsgiApp(object):
    def __init__(self):
        print('WsgiApp init')

    @webob.dec.wsgify
    def __call__(self, req):
        print('WsgiApp::__call__ start')
        print_req_env(req)
        res = Response()
        res.content_type = 'application/json'
        res.body = json.dumps(req.json, indent=4, sort_keys=True)
        return res


class WsgiMiddle01(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle01 init')

    @webob.dec.wsgify
    def __call__(self, req):
        print('WsgiMiddle01::__call__ start')
        res = req.get_response(self.app)
        print('WsgiMiddle01::__call__ After call its app')
        return res


class WsgiMiddle02(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle02 init')

    @webob.dec.wsgify
    def __call__(self, req):
        print('WsgiMiddle02::__call__ start')
        res = req.get_response(self.app)
        print('WsgiMiddle02::__call__ After call its app')
        return res


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
