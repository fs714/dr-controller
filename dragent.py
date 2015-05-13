import webob.dec
from webob import Response


def dr_agent_factory(global_conf, **local_conf):
    return DrAgent(global_conf, local_conf)


class DrAgent(object):
    def __init__(self, global_conf, local_conf):
        self.global_conf = global_conf
        self.local_conf = local_conf

    @webob.dec.wsgify
    def __call__(self, req):
        res = Response()
        res.content_type = 'text/plain'
        parts = []
        for name, value in sorted(req.environ.items()):
            parts.append('%s: %r' % (name, value))
        res.body = '\n'.join(parts)
        res.body += '\n'

        return res
