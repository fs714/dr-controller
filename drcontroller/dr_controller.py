import webob.dec
import routes
import routes.middleware
import logging
import os
import sys
from wsgi_util import RoutesMiddleware
from replication.controller.nova_handler import NovaHandler
from replication.controller.neutron_handler import NeutronHandler
from replication.controller.glance_handler import GlanceHandler
from recovery.recovery_handler import RecoveryHandler


def dr_controller_factory(global_conf, **local_conf):
    return DrController(global_conf, local_conf)


class DrController(object):
    def __init__(self, global_conf, local_conf):
        self.global_conf = global_conf
        self.local_conf = local_conf
        self.logger = logging.getLogger("DrController")
        self.logger.info("Init DrController")

        self.mapper = routes.Mapper()

        nova_controller = RoutesMiddleware(NovaHandler())
        self.mapper.connect("nova", "/nova",
                            controller=nova_controller, action="accept",
                            conditions=dict(method=["POST"]))

        neutron_controller = RoutesMiddleware(NeutronHandler())
        self.mapper.connect("neutron", "/neutron",
                            controller=neutron_controller, action="accept",
                            conditions=dict(method=["POST"]))

        glance_controller = RoutesMiddleware(GlanceHandler())
        self.mapper.connect("glance", "/glance",
                            controller=glance_controller, action="accept",
                            conditions=dict(method=["POST"]))

        recovery_controller = RoutesMiddleware(RecoveryHandler())
        self.mapper.connect("recovery", "/recovery/start",
                            controller=recovery_controller, action="start",
                            conditions=dict(method=["POST"]))

        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.mapper)

    @webob.dec.wsgify
    def __call__(self, req):
        """
        res = Response()
        res.content_type = 'application/json'
        res.body = json.dumps(req.environ['updated_env'],
                              indent=4, sort_keys=True)
        """
        return self._router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            implemented_http_methods = ['GET', 'HEAD', 'POST', 'PUT',
                                        'DELETE', 'PATCH']
            if req.environ['REQUEST_METHOD'] not in implemented_http_methods:
                return webob.exc.HTTPNotImplemented()
            else:
                return webob.exc.HTTPNotFound()
        app = match['controller']
        return app
