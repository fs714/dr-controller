import logging
import pdb
import string, os, sys, time
import keystoneclient.v2_0.client as keystoneclient
import glanceclient
import ConfigParser

# set_conf = "/home/eshufan/project/drcontroller/drcontroller/conf/set.conf"
# DRF = "drf"
# DRC = "drc"
# LOCAL_URL = "http://192.168.56.200:10081"
# handle_type = nova, glance or neutron
# key_service_type = {'glance':'image', 'nova':'', 'neutron':''}

class BaseHandler(object)
    def __init__(self, set_conf, handle_type):
        self.set_conf = set_conf
        self.handle_type

    def keystone_handle(self, key_type, sevice_type, endpoint_type):
        cf = ConfigParser.ConfigParser()
        cf.read(set_conf)
        keystone = keystoneclient.Client(auth_url=cf.get(key_type,"auth_url"),
                                         username=cf.get(key_type,"user"),
                                         password=cf.get(key_type,"password"),
                                         tenant_name=cf.get(key_type,"tenant_name"))
        endpoint = keystone.service_catalog.url_for(service_type=service_type, endpoint_type=endpoint_type)
        return endpoint, keystone.auth_token

    def post_handle(self, message):
        endpoint, auth_token = self.keystone_handle('drf', service_type='image', endpoint_type='publicURL')
        drf_glance = glanceclient.Client('1',endpoint, token=auth_token)
        image_id = message['Response']['image']['id']
        status = drf_glance.images.get(image_id).status
        while (status != 'active')  and (status != 'killed'):
            time.sleep(1)
            status = drf_glance.images.get(image_id).status
            if status == 'active':
                pdb.set_trace()
                url = 'http://192.168.56.200:10081/images/'+image_id
                endpoint, auth_token = self.keystone_handle('drc', service_type='image', endpoint_type='publicURL')
                drc_glance = glanceclient.Client('1', endpoint, token=auth_token)
                image = drc_glance.images.create(name = message['Response']['image']['name'],
                                                 container_format = message['Response']['image']['container_format'],
                                                 min_ram = message['Response']['image']['min_ram'],
                                                 disk_format = message['Response']['image']['disk_format'],
                                                 min_disk =  message['Response']['image']['min_disk'],
                                                 protected = str(message['Response']['image']['protected']),
                                                 is_public = str( message['Response']['image']['is_public']),
                                                 owner = message['Response']['image']['owner'],
                                                 location = url ,
                                                 size = message['Response']['image']['size'] )

    def delete_handle(message):
        errlog = logging.getLogger("GlanceHandler:accept")
        endpoint, auth_token = self.keystone_handle('drc', service_type='image',endpoint_type='pyblicURL')
        drc_glance = glanceclient.Client('2', endpoint, token=auth_token)
        url = message['Request']['url'].split('/')
        image_id = url[-1]
        try:
            drc_glance.images.get('01fc6be8-c2a9-4e22-b574-b4638fa3dead')
        except:
            errlog.debug('no such image')
        else:
            drc_glance.images.delete('01fc6be8-c2a9-4e22-b574-b4638fa3dead')

    def put_handle(message):
        endpoint, auth_token = self.keystone_handle("drf", service_type='image', endpoint_type='publicURL')
        drf_glance = glanceclient.Client('1', endpoint, token=auth_token)
        image_id = message['Response']['image']['id']
        status = drf_glance.images.get(image_id).status
        while (status != 'active')  and (status != 'killed'):
            time.sleep(1)
            status = drf_glance.images.get(image_id).status
        if status == 'active':
            pdb.set_trace()
            url = 'http://192.168.56.200:10081/images/'+image_id
            endpoint, auth_token = self.keystone_handle("drc", service='image', endpoint_type='publicURL')
            drc_glance = glanceclient.Client('1', endpoint, token=auth_token)
            image = drc_glance.images.update(image_id = image_id,
                                             remove_props = None,
                                             name = message['Response']['image']['name'],
                                             container_format = message['Response']['image']['container_format'],
                                             min_ram = message['Response']['image']['min_ram'],
                                             disk_format = message['Response']['image']['disk_format'],
                                             min_disk =  message['Response']['image']['min_disk'],
                                             protected = str(message['Response']['image']['protected']),
                                             is_public = str( message['Response']['image']['is_public']),
                                             owner = message['Response']['image']['owner'],
                                             location = url ,
                                             size = message['Response']['image']['size'] )

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__+":accept")
        if len(req)>0:
           for i in range(0,len(req)):
               if req[i] != {}:
                  env=req[i].body
                  if len(env)>0 :
                     message=eval(env.replace('null','None').replace('false','False').replace('true','True'))
                     if message['Request']['type'] == 'POST':
                        self.post_handle(message)
                        print 'post'
                     elif message['Request']['type'] == 'DELETE':
                        self.delete_handle(message)
                        print 'delete'
                     elif message['Request']['type'] == 'PUT':
                        self.put_handle(message)
                        print 'put'
        self.logger.info("--- Hello "+handle_type+" ---")
        return ['Hello'+handle_type]
