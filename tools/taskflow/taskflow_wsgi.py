import json
import logging
import webob.dec
import eventlet
from eventlet import wsgi
from webob import Response
from simple_task import AnsibleTask
from taskflow import engines
from taskflow.patterns import linear_flow, unordered_flow


class WsgiApp(object):
    def __init__(self):
        print('WsgiApp init')

    @webob.dec.wsgify
    def __call__(self, req):
        print('WsgiApp::__call__ start')
        print_req_env(req)
        self.start()
        res = Response()
        res.content_type = 'application/json'
        res.body = json.dumps('{Hello: World}', indent=4, sort_keys=True)
        return res

    def start(self):
        hosts = ['10.175.150.16']
        module_name = 'shell'
        module_args = 'echo "Hello World"'
        pattern = '*'

        linearflow = linear_flow.Flow('Liner_Flow')
        unorderedflow = unordered_flow.Flow('Unordered_Flow')

        for i in range(0, 5):
            linear_task_name = 'Linear_task_' + str(i)
            linear_task = AnsibleTask(linear_task_name, hosts, module_name,
                                      module_args, pattern)
            unordered_task_name = 'Unordered_task_' + str(i)
            unordered_task = AnsibleTask(unordered_task_name, hosts,
                                         module_name, module_args, pattern)
            linearflow.add(linear_task)
            unorderedflow.add(unordered_task)

        flow = linear_flow.Flow('Final_Flow')
        flow.add(linearflow, unorderedflow)

        eng = engines.load(flow)
        eng.run()


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
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Main")

    app = WsgiMiddle01(WsgiMiddle02(WsgiApp()))
    wsgi.server(eventlet.listen(('', 80)), app)


if __name__ == '__main__':
    main()
