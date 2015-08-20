import logging
import string, os, sys, time
import keystoneclient.v2_0.client as keystoneclient
import ConfigParser
import pdb

class BaseHandler(object):
    def __init__(self, set_conf):
        self.set_conf = set_conf

    def keystone_handle(self, key_type, service_type, endpoint_type):
        cf = ConfigParser.ConfigParser()
        cf.read(self.set_conf)
        keystone = keystoneclient.Client(auth_url=cf.get(key_type,"auth_url"),
                                         username=cf.get(key_type,"user"),
                                         password=cf.get(key_type,"password"),
                                         tenant_name=cf.get(key_type,"tenant_name"))
        endpoint = keystone.service_catalog.url_for(service_type=service_type, endpoint_type=endpoint_type)
#        pdb.set_trace()
        return endpoint, keystone.auth_token

    def post_handle(self, message):
        pass

    def delete_handle(message):
        pass

    def put_handle(message):
        pass

