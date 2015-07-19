import logging


class RecoveryHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("RecoveryHandler")
        self.logger.info('Init RecoveryHandler')

    def start(self, *req, **kwargs):
        self.logger = logging.getLogger("RecoveryHandler:start")

        self.logger.info("--- Hello Recovery ---")
        return ['Hello Recovery']
