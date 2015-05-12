import logging
import logging.config
from urllib import quote


class record_url:
    def __init__(self):
        logging.config.fileConfig("logging.conf")
        self.logger = logging.getLogger("record_url")

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        url = self.url_reconstruction(environ)
        self.logger.info("--------------------------------")
        self.logger.info(url)
        self.logger.info("------")
        for key, value in environ.items():
            self.logger.info(key + " = " + str(value))
        return [url + '\n']

    def url_reconstruction(self, environ):
        url = environ['wsgi.url_scheme']+'://'

        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']

            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
                else:
                    if environ['SERVER_PORT'] != '80':
                        url += ':' + environ['SERVER_PORT']

        url += quote(environ.get('SCRIPT_NAME', ''))
        url += quote(environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
        return url
