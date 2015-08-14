import logging

def post_handle(message):
    pass

def delete_handle(message):
    pass

def put_handle(mesage):
    pass


class NeutronHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("NeutronHandler")
        self.logger.info('Init NeutronHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("NeutronHandler:accept")

        self.logger.info("--- Hello Neutron ---")
        return ['Hello Neutron']
