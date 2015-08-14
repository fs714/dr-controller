import logging
import pdb
import time
import keystoneclient.v2_0.client as keystoneclient
from glanceclient import Client
import glanceclient
import ConfigParser
import string,os,sys
import os

def post_handle(message):
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/project/drcontroller/drcontroller/conf/set.conf")
    drf_keystone = keystoneclient.Client(auth_url=cf.get("drf","auth_url"),
                           username= cf.get("drf","user"),
                           password= cf.get("drf","password"),
                           tenant_name=cf.get("drf","tenant_name"))
    drf_glance_endpoint = drf_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    drf_glance = glanceclient.Client('1',drf_glance_endpoint, token=drf_keystone.auth_token)
    image_id=message['Response']['image']['id']   
    status=drf_glance.images.get(image_id).status
    while (status != 'active')  and (status != 'killed'):
        time.sleep(1)
        status=drf_glance.images.get(image_id).status
    if status == 'active':
        pdb.set_trace()
        url='http://192.168.56.200:10081/images/'+image_id
        drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
        drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
        drc_glance = glanceclient.Client('1',drc_glance_endpoint, token=drc_keystone.auth_token)
        image=drc_glance.images.create(name = message['Response']['image']['name'],
                                 container_format = message['Response']['image']['container_format'],
                                 min_ram = message['Response']['image']['min_ram'],
                                 disk_format = message['Response']['image']['disk_format'], 
                                 min_disk =  message['Response']['image']['min_disk'],
                                 protected = str(message['Response']['image']['protected']),
                                 is_public = str( message['Response']['image']['is_public']),
                                 owner = message['Response']['image']['owner'],
                                 location = url ,
                                 size=message['Response']['image']['size']                 )      


def delete_handle(message):
    errlog = logging.getLogger("GlanceHandler:accept")
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/project/drcontroller/drcontroller/conf/set.conf")
    drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
    drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    drc_glance = glanceclient.Client('2',drc_glance_endpoint, token=drc_keystone.auth_token)
    url=message['Request']['url'].split('/')
    image_id=url[len(url)-1] 
    try:
        drc_glance.images.get('01fc6be8-c2a9-4e22-b574-b4638fa3dead')
    except:
        errlog.debug('no such image') 
    else:
        drc_glance.images.delete('01fc6be8-c2a9-4e22-b574-b4638fa3dead')


def put_handle(message):
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/project/drcontroller/drcontroller/conf/set.conf")
    drf_keystone = keystoneclient.Client(auth_url=cf.get("drf","auth_url"),
                           username= cf.get("drf","user"),
                           password= cf.get("drf","password"),
                           tenant_name=cf.get("drf","tenant_name"))
    drf_glance_endpoint = drf_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    drf_glance = glanceclient.Client('1',drf_glance_endpoint, token=drf_keystone.auth_token)
    image_id=message['Response']['image']['id']
    status=drf_glance.images.get(image_id).status
    while (status != 'active')  and (status != 'killed'):
        time.sleep(1)
        status=drf_glance.images.get(image_id).status
    if status == 'active':
        pdb.set_trace()
        url='http://192.168.56.200:10081/images/'+image_id
        drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
        drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
        drc_glance = glanceclient.Client('1',drc_glance_endpoint, token=drc_keystone.auth_token)
        image=drc_glance.images.update(image_id=image_id,
                                 remove_props=None,
                                 name = message['Response']['image']['name'],
                                 container_format = message['Response']['image']['container_format'],
                                 min_ram = message['Response']['image']['min_ram'],
                                 disk_format = message['Response']['image']['disk_format'],
                                 min_disk =  message['Response']['image']['min_disk'],
                                 protected = str(message['Response']['image']['protected']),
                                 is_public = str( message['Response']['image']['is_public']),
                                 owner = message['Response']['image']['owner'],
                                 location = url ,
                                 size=message['Response']['image']['size'] )


                         
class GlanceHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("GlanceHandler")
        self.logger.info('Init GlanceHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("GlanceHandler:accept")
        if len(req)>0:
           for i in range(0,len(req)):
               if req[i] != {}:
                  env=req[i].body
                  if len(env)>0 :
                     message=eval(env.replace('null','None').replace('false','False').replace('true','True'))    
                     if message['Request']['type']=='POST':
#                        post_handle(message)
                        print 'post'
                     elif message['Request']['type']=='DELETE':
#                        delete_handle(message)
                        print 'delete'            
        self.logger.info("--- Hello Glance ---")
        return ['Hello Glance']
