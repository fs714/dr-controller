import logging


class GlanceHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("GlanceHandler")
        self.logger.info('Init GlanceHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("GlanceHandler:accept")

        self.logger.info("--- Hello Glance ---")
        return ['Hello Glance']
