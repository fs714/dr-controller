import json
from webob.dec import wsgify
from webob import Response


class RoutesMiddleware(object):
    def __init__(self, controller):
        self.controller = controller

    @wsgify
    def __call__(self, request):
        action_args = self.get_action_args(request.environ)
        action = action_args.pop('action', None)
        action_result = self.dispatch(self.controller, action,
                                      request, action_args)

        res = Response()
        res.content_type = 'application/json'
        res.body = json.dumps(action_result, indent=4, sort_keys=True)

        return res

    def dispatch(self, obj, action, *args, **kwargs):
        try:
            method = getattr(obj, action)
        except AttributeError:
            method = getattr(obj, 'default')

        return method(*args, **kwargs)

    def get_action_args(self, request_environment):
        try:
            args = request_environment['wsgiorg.routing_args'][1].copy()
        except Exception:
            return {}

        try:
            del args['controller']
        except KeyError:
            pass

        try:
            del args['format']
        except KeyError:
            pass

        return args
