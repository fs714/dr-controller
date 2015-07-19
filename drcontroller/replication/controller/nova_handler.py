import logging


class NovaHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("NovaHandler")
        self.logger.info('Init NovaHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("NovaHandler:accept")

        self.logger.info("--- Hello Nova ---")
        return ['Hello Nova']
