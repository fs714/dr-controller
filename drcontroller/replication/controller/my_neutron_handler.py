import logging
import base_handler

class NeutronHandler(base_handler.BaseHandler):
    def __init__(self, set_conf, handle_type):
        '''
        set_conf: the configuration file path of keystone authorization
        handle_type: the handle service type, eg, glance, nova, neutron
        '''
        self.logger = logging.getLogger("NeutronHandler")
        self.logger.info('Init NeutronHandler')
        super(NeutronHandler, self).__init__(set_conf, handle_type)

