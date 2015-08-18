import logging


class NeutronHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("NeutronHandler")
        self.logger.info('Init NeutronHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("NeutronHandler:accept")

        self.logger.info("--- Hello Neutron ---")
        return ['Hello Neutron']
