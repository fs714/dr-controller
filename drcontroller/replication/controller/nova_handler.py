#/usr/bin/env python2.7
from db_Dao import DRGlanceDao, DRNovaDao, DRNeutronNetDao,DRNeutronPortDao
from models import Base, DRGlance, DRNova, DRNeutronNet,DRNeutronPort
import logging
import pdb
import time
import keystoneclient.v2_0.client as keystoneclient
import novaclient.v1_1.client as novaclient
import glanceclient
import ConfigParser
import string,os,sys
import re

def change_post_handle(message):
    changelog = logging.getLogger("NovaHandler:accept")
    changelog.info("change_post_handle")
    cf=ConfigParser.ConfigParser()
    novaDao = DRNovaDao()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    drf_ncred={}
    drf_ncred['auth_url']= cf.get("drf","auth_url")
    drf_ncred['username']= cf.get("drf","user")
    drf_ncred['api_key'] = cf.get("drf","password")
    drf_ncred['project_id']=cf.get("drf","tenant_name")
    drf_nova = novaclient.Client(**drf_ncred)
#    print "drf:", drf_glance_endpoint
    url=message['Request']['url'].split('/')
    server_id=url[len(url)-2]

    if (message["Request"]["wsgi.input"].has_key("os-stop")):
            drf_server=drf_nova.servers.get(server_id)
            status=drf_server.status
            pow_status=drf_server.to_dict()['OS-EXT-STS:power_state']
            count=0
            while ((status != "SHUTOFF" ) or (pow_status != 4)) :
                time.sleep(1)
                drf_server=drf_nova.servers.get(server_id)
                status=drf_server.status
                pow_status=drf_server.to_dict()['OS-EXT-STS:power_state']
                count+=1
                if (count==180):
                    return
            try:
                novaDao.update_by_primary_instance__uuid(server_id,{"status":"SHUTOFF"})
                changelog.info(server_id)
                changelog.info(novaDao.get_by_primary_instance_uuid(server_id).status)
            except:
                return

    if (message["Request"]["wsgi.input"].has_key("os-start")):
            drf_server=drf_nova.servers.get(server_id)
            status=drf_server.status
            pow_status=drf_server.to_dict()['OS-EXT-STS:power_state']
            count=0
            while ((status != "ACTIVE" ) or (pow_status != 1)) :
                time.sleep(1)
                drf_server=drf_nova.servers.get(server_id)
                status=drf_server.status
                pow_status=drf_server.to_dict()['OS-EXT-STS:power_state']
                count+=1
                if (count==60):
                    return
            try:
                novaDao.update_by_primary_instance__uuid(server_id,{"status":"ACTIVE"})
                changelog.info(server_id)
                changelog.info(novaDao.get_by_primary_instance_uuid(server_id).status)
            except:
                return

def post_handle(message):
    cf=ConfigParser.ConfigParser()
    novaDao = DRNovaDao()
    glanceDao = DRGlanceDao()
    neutronNetDao = DRNeutronNetDao()
    neutronPortDao = DRNeutronPortDao()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    drf_ncred={}
    drf_ncred['auth_url']= cf.get("drf","auth_url")
    drf_ncred['username']= cf.get("drf","user")
    drf_ncred['api_key'] = cf.get("drf","password")
    drf_ncred['project_id']=cf.get("drf","tenant_name")
    drf_nova = novaclient.Client(**drf_ncred)
#    print "drf:", drf_glance_endpoint
    url=message['Request']['url'].split('/')
    server_id=message['Response']['server']['id']
    status=drf_nova.servers.get(server_id).status
    host_id=drf_nova.servers.get(server_id).to_dict()['OS-EXT-SRV-ATTR:host']
    while (status == "BUILD" ):
        time.sleep(1)
        status=drf_nova.servers.get(server_id).status
    max_wait_time = 10
    counter = 0
    while(len(drf_nova.servers.interface_list(server_id)) == 0):
        time.sleep(1)
        if counter > max_wait_time:
            return
        counter += 1
    port_id=drf_nova.servers.interface_list(server_id)[0].port_id
    if (status == "ACTIVE"):
        drc_ncred={}
        drc_ncred['auth_url']= cf.get("drc","auth_url")
        drc_ncred['username']= cf.get("drc","user")
        drc_ncred['api_key'] = cf.get("drc","password")
        drc_ncred['project_id']=cf.get("drc","tenant_name")
        drc_nova = novaclient.Client(**drc_ncred)
        image_id = message['Request']['wsgi.input']['server']['imageRef']
        net_id = message['Request']['wsgi.input']['server']['networks'][0]['uuid']
        drc_image = glanceDao.get_by_primary_uuid(image_id).secondary_uuid
        drc_net = neutronNetDao.get_by_primary_uuid(net_id).secondary_uuid
        if (message['Request']['wsgi.input']['server'].has_key('networks')):
            drc_server=drc_nova.servers.create(name=message['Request']['wsgi.input']['server']['name']+"_shadow",
                                    image=drc_image,
                                    flavor=message['Request']['wsgi.input']['server']['flavorRef'],
                                    min_count=message['Request']['wsgi.input']['server']['min_count'],
                                    max_count=message['Request']['wsgi.input']['server']['max_count'],
                                    nics=[{'net-id':drc_net}]
            )
        else:
            drc_server=drc_nova.servers.create(name=message['Request']['wsgi.input']['server']['name'],
                                    image=drc_image,
                                    flavor=message['Request']['wsgi.input']['server']['flavorRef'],
                                    min_count=message['Request']['wsgi.input']['server']['min_count'],
                                    max_count=message['Request']['wsgi.input']['server']['max_count']
            )
        status=drc_nova.servers.get(drc_server.id).status
        drc_host_id=drf_nova.servers.get(server_id).to_dict()['OS-EXT-SRV-ATTR:host']
        max_wait_time = 10
        counter = 0
        while(len(drc_nova.servers.interface_list(drc_server.id)) == 0):
            time.sleep(1)
            if counter > max_wait_time:
                return
            counter += 1
        drc_port_id=drc_nova.servers.interface_list(drc_server.id)[0].port_id
        port=DRNeutronPort(primary_uuid=port_id, secondary_uuid=drc_port_id)
        nova= DRNova(primary_instance_uuid=server_id,
                     secondary_instance_uuid=drc_server.id,
                     primary_image_uuid=image_id,
                     secondary_image_uuid=drc_image,
                     primary_node_name=host_id,
                     secondary_node_name=drc_host_id,
                     status='ACTIVE')
        nova.ports.append(port)
        novaDao.add(nova)
        #neutronPortDao.add(DRNeutronPort(primary_uuid=port_id,
        #                                 secondary_uuid=drc_port_id
        #))
        while (status == "BUILD" ):
            time.sleep(1)
            status=drc_nova.servers.get(drc_server.id).status
        if (status == "ACTIVE"):
            drc_nova.servers.stop(drc_server.id)


def delete_handle(message):
    novaDao = DRNovaDao()
    errlog = logging.getLogger("NovaHandler:accept")
    url=message['Request']['url'].split('/')
    server_id=url[len(url)-1]
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    try:
        drc_id = novaDao.get_by_primary_instance_uuid(server_id).secondary_instance_uuid
    except:
        return
    if (drc_id != None):
        drc_ncred={}
        drc_ncred['auth_url']= cf.get("drc","auth_url")
        drc_ncred['username']= cf.get("drc","user")
        drc_ncred['api_key'] = cf.get("drc","password")
        drc_ncred['project_id']=cf.get("drc","tenant_name")
        drc_nova = novaclient.Client(**drc_ncred)
        drc_nova.servers.delete(drc_id)
        novaDao.delete_by_primary_instance_uuid(server_id)





class NovaHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("NovaHandler")
        self.logger.info('Init NovaHandler')

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("NovaHandler:accept")
        if len(req)>0:
           for i in range(0,len(req)):
               if req[i] != {}:
                  env=req[i].body
                  if len(env)>0:
                     message=eval(env.replace('null','None').replace('false','False').replace('true','True'))
                     if message['Request']['type']=='POST':
                        pattern = re.compile(r'http://.*/v./.{32}/servers/.{36}/action$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            change_post_handle(message)
                        pattern = re.compile(r'http://.*/v./.{32}/servers$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            post_handle(message)
                     elif message['Request']['type']=='DELETE':
                        pattern = re.compile(r'http://.*/v./.{32}/servers/.{36}$')
                        match = pattern.match(message['Request']['url'])
                        if match:
                            delete_handle(message)
        self.logger.info("--- Hello Nova ---")
        return ['Hello Nova']
