import logging
import string, os, sys, time
import pdb
from neutronclient.neutron import client as neutron_client
import base_handler


set_conf = "/home/eshufan/project/drcontroller/drcontroller/conf/set.conf"
handle_type = "Neutron"

class NeutronApp(base_handler.BaseHandler):

    def __init__(self, set_conf, handle_type):
        super(NeutronApp, self).__init__(set_conf)
        self.handle_type = handle_type

    def post_handle(self, message):
        '''
        Create a network.
        '''
        endpoint, auth_token = self.keystone_handle('drf', service_type='network', endpoint_type='publicURL')
        drf_neutron = neutron_client.Client('2.0', endpoint, token=auth_token)
        drf_network_id = message['Response']['network']['id']
        drf_network_name = message['Response']['network']['name']
        status = drf__neutron.list_networks(name=drf_network_name)['networks'][0]['status']
        while (status != 'active')  and (status != 'killed'):
            time.sleep(1)
            status = drf__neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            if status == 'active':
                pdb.set_trace()
                endpoint, auth_token = self.keystone_handle('drc', service_type='network', endpoint_type='publicURL')
                drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                  'mtu':message['Response']['network']['mtu'],
                                  'name':'_'.join([drf_network_name,'shadow'])
                                  'provider:network_type':message['Response']['network']['provider:network_type'],
                                  'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                  'router:external':message['Response']['network']['router:external'],
                                  'shared':message['Resopnse']['network']['shared'],
                                  'status':message['Resopnse']['network']['status'],
                                  'subnets':message['Response']['network']['subnets'],
                                  'tenant_id':message['Response']['network']['tenant_id']
                                  }
                drc_neutron.create_network({'network':network_params})
                networks = drc_neutron.list_networks(name=network_params['name'])
                drc_network_id = networks['networks'][0]['id']
                # add <drf_network_id, drc_network_id,status> to DB

    def delete_handle(message):
        errlog = logging.getLogger("NeutronHandler:accept")
        endpoint, auth_token = self.keystone_handle('drc', service_type='network',endpoint_type='pyblicURL')
        drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
        url = message['Request']['url'].split('/')
        network_id = url[-1].split('.')[0]
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
class NeutronHandler(object):
    def __init__(self):
        self.neutron_app = NeutronApp(set_conf, handle_type)

    def accept(self, *req, **kwargs):
        self.logger = logging.getLogger("NeutronHandler:accept")
        if len(req)>0:
           for i in range(0,len(req)):
               if req[i] != {}:
                  env=req[i].body
                  if len(env)>0 :
                     message=eval(env.replace('null','None').replace('false','False').replace('true','True'))
                     if message['Request']['type'] == 'POST':
     #                   self.neutron_app.post_handle(message)
                        print 'post'
                     elif message['Request']['type'] == 'DELETE':
    #                    self.delete_handle(message)
                        print 'delete'
                     elif message['Request']['type'] == 'PUT':
    #                    self.neutron_app.put_handle(message)
                        print 'put'
        self.logger.info("--- Hello Neutron ---")
        return ['Hello Neutron']
