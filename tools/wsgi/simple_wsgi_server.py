import eventlet
from eventlet import wsgi


class WsgiApp(object):
    def __init__(self):
        print('WsgiApp init')

    def __call__(self, environ, start_response):
        print('WsgiApp::__call__ start')
        print_wsgi_env(environ)
        body = environ['wsgi.input'].read(environ['CONTENT_LENGTH'])
        print('WsgiApp::__call__ before start_response')
        start_response('200 OK', [('Content-Type', 'application/json')])
        print('WsgiApp::__call__ after start_response')
        return body


class WsgiMiddle01(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle01 init')

    def __call__(self, environ, start_response):
        print('WsgiMiddle01::__call__ start')
        result = self.app(environ, start_response)
        print('WsgiMiddle01::__call__ After call its app')
        return result


class WsgiMiddle02(object):
    def __init__(self, app):
        self.app = app
        print('WsgiMiddle02 init')

    def __call__(self, environ, start_response):
        print('WsgiMiddle02::__call__ start')
        result = self.app(environ, start_response)
        print('WsgiMiddle02::__call__ After call its app')
        return result


def print_wsgi_env(env):
    for name, value in sorted(env.items()):
        print(name + " = " + str(value))
    return env


def main():
    app = WsgiMiddle01(WsgiMiddle02(WsgiApp()))
    wsgi.server(eventlet.listen(('', 80)), app)


if __name__ == '__main__':
    main()
