#/usr/bin/env python2.7
from db.db_Dao import DRGlanceDao, DRNovaDao
from db.models import Base, DRGlance, DRNova
import logging
import pdb
import time
import keystoneclient.v2_0.client as keystoneclient
from glanceclient import Client
import glanceclient
import ConfigParser
import string,os,sys
import re

def post_handle(message):
    cf=ConfigParser.ConfigParser()
    errlogger = logging.getLogger("GlanceHandler:accept")
    glanceDao = DRGlanceDao()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    drf_keystone = keystoneclient.Client(auth_url=cf.get("drf","auth_url"),
                           username= cf.get("drf","user"),
                           password= cf.get("drf","password"),
                           tenant_name=cf.get("drf","tenant_name"))
    drf_glance_endpoint = drf_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    drf_glance = glanceclient.Client('1',drf_glance_endpoint, token=drf_keystone.auth_token)
#    print "drf:", drf_glance_endpoint
#    pdb.set_trace()
    image_id=message['Response']['image']['id']
    status = message['Response']['image']['status']
#   status=drf_glance.images.get(image_id).status
#    count=0
#    while (status != 'active')  and (status != 'killed'):
#        time.sleep(1)
#        if status == 'queued':
#            count +=1
#        else:
#            count = 0
#        if  count == 5:
#            glanceDao.add(DRGlance(primary_uuid=image_id,status='queued'))
#            break
#        status=drf_glance.images.get(image_id).status


    if status == 'queued':
       glanceDao.add(DRGlance(primary_uuid=image_id,status='queued'))
    if status == 'active':
        new_data=drf_glance.images.data(image_id)._resp
        drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
        drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
        drc_glance = glanceclient.Client('1',drc_glance_endpoint, token=drc_keystone.auth_token)
        image=drc_glance.images.create(name = message['Response']['image']['name']+"_shadow",
                                 container_format = message['Response']['image']['container_format'],
                                 min_ram = message['Response']['image']['min_ram'],
                                 disk_format = message['Response']['image']['disk_format'],
                                 min_disk =  message['Response']['image']['min_disk'],
                                 protected = str(message['Response']['image']['protected']),
                                 is_public = str( message['Response']['image']['is_public']),
                                 owner = message['Response']['image']['owner'],
                                 data = new_data                )
        glanceDao.add(DRGlance(primary_uuid=image_id,secondary_uuid=image.id,status='active'))
        errlogger.info("#####################################################")
        errlogger.info(image_id)
        errlogger.info(glanceDao.get_by_primary_uuid(image_id).secondary_uuid)

def delete_handle(message):
    glanceDao = DRGlanceDao()
    errlog = logging.getLogger("GlanceHandler:accept")
    url=message['Request']['url'].split('/')
    image_id=url[len(url)-1]
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")

    try:
        drc_id = glanceDao.get_by_primary_uuid(image_id).secondary_uuid
    except:
        return
#    drf_keystone = keystoneclient.Client(auth_url=cf.get("drf","auth_url"),
#                           username= cf.get("drf","user"),
#                           password= cf.get("drf","password"),
#                           tenant_name=cf.get("drf","tenant_name"))
#    drf_glance_endpoint = drf_keystone.service_catalog.url_for(service_type='image',
#                                                   endpoint_type='publicURL')
#    drf_glance = glanceclient.Client('1',drf_glance_endpoint, token=drf_keystone.auth_token)

#    status=drf_glance.images.get(image_id).status
#    count=0
#    while (status != 'deleted'):
#        time.sleep(1)
#        count +=1
#        if  count == 5:
#            break
#        status=drf_glance.images.get(image_id).status
#    if status == 'deleted':

    drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
    drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
    drc_glance = glanceclient.Client('2',drc_glance_endpoint, token=drc_keystone.auth_token)
    if (drc_id != None):
        drc_glance.images.delete(drc_id)
        glanceDao.delete_by_primary_uuid(image_id)


def put_handle(message):
    glanceDao = DRGlanceDao()
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    image_id=message['Response']['image']['id']
    try:
        glancedb= glanceDao.get_by_primary_uuid(image_id)
        gl_status=glancedb.status
    except:
        return
    if gl_status=='queued':
        drf_keystone = keystoneclient.Client(auth_url=cf.get("drf","auth_url"),
                           username= cf.get("drf","user"),
                           password= cf.get("drf","password"),
                           tenant_name=cf.get("drf","tenant_name"))
        drf_glance_endpoint = drf_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
        drf_glance = glanceclient.Client('1',drf_glance_endpoint, token=drf_keystone.auth_token)
#        status=drf_glance.images.get(image_id).status
#        count=0
#        while (status != 'active')  and (status != 'killed'):
#            time.sleep(1)
#            if status == 'queued':
#               count +=1
#            else:
#               count = 0
#            if  count == 5:
#               break
#            status=drf_glance.images.get(image_id).status
        status=message['Response']['image']['status']
        if status == 'active':
            new_data=drf_glance.images.data(image_id)._resp
            drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
            drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
            drc_glance = glanceclient.Client('1',drc_glance_endpoint, token=drc_keystone.auth_token)
            image=drc_glance.images.create(name = message['Response']['image']['name']+"_shadow",
                                 container_format = message['Response']['image']['container_format'],
                                 min_ram = message['Response']['image']['min_ram'],
                                 disk_format = message['Response']['image']['disk_format'],
                                 min_disk =  message['Response']['image']['min_disk'],
                                 protected = str(message['Response']['image']['protected']),
                                 is_public = str( message['Response']['image']['is_public']),
                                 owner = message['Response']['image']['owner'],
                                 data = new_data )
            glanceDao.delete_by_primary_uuid(image_id)
            glanceDao.add(DRGlance(primary_uuid=image_id,secondary_uuid=image.id,status='active'))

    if gl_status=='active':
        try:
            drc_id = glanceDao.get_by_primary_uuid(image_id).secondary_uuid
        except:
            return
        drc_keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                           username= cf.get("drc","user"),
                           password= cf.get("drc","password"),
                           tenant_name=cf.get("drc","tenant_name"))
        drc_glance_endpoint = drc_keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
        drc_glance = glanceclient.Client('1',drc_glance_endpoint, token=drc_keystone.auth_token)
        image=drc_glance.images.update(image=drc_id,
                                 name = message['Response']['image']['name']+"_shadow",
                                 container_format = message['Response']['image']['container_format'],
                                 min_ram = message['Response']['image']['min_ram'],
                                 disk_format = message['Response']['image']['disk_format'],
                                 min_disk =  message['Response']['image']['min_disk'],
                                 protected = str(message['Response']['image']['protected']),
                                 is_public = str( message['Response']['image']['is_public']),
                                 owner = message['Response']['image']['owner']
                                 )

def test():
    changelog = logging.getLogger("GlanceHandler:accept")
    changelog.info("testhandle")
    novaDao = DRNovaDao(DRNova)
    changelog.info(novaDao.get_by_primary_uuid("test").secondary_uuid)


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
                  if len(env)>0:
                     message = eval(env.replace('null','None').replace('false','False').replace('true','True'))
                     if message['Request']['type']=='POST':
                        pattern = re.compile(r'http://.*/v./images$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            post_handle(message)
                     elif message['Request']['type']=='DELETE':
                        pattern = re.compile(r'http://.*/v./images/.{36}$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            delete_handle(message)
                     else:
                        pattern = re.compile(r'http://.*/v./images/.{36}$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            put_handle(message)
        self.logger.info("--- Hello Glance ---")
        return ['Hello Glance']
