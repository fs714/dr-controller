import logging
import string, os, sys, time
import pdb
from neutronclient.neutron import client as neutron_client
import base_handler
from db_Dao import DRNeutron
from models import Base,DRNeutro

set_conf = "/home/eshufan/project/drcontroller/drcontroller/conf/set.conf"
handle_type = "Neutron"

class NeutronApp(base_handler.BaseHandler):

    def __init__(self, set_conf, handle_type):
        super(NeutronApp, self).__init__(set_conf)
        self.handle_type = handle_type

    def get_network_type(self, message):
        '''
        Get the network type for 'networks' or 'subnets'
        '''
        request_type = message['Request']['type']
        if request_type == 'POST':
            url = message['Request']['url'].split('/')
            network_type= url[-1].split('.')[0]
            return network_type
        elif request_type == 'DELETE':
            url = message['Request']['url'].split('/')
            network_type= url[-2]
            return network_type
        elif request_type == 'PUT':
            url = message['Request']['url'].split('/')
            network_type= url[-2]
            return network_type
        else:
            return 'error_network_type'

    def post_handle(self, message):
        '''
        Create a network.
        '''
        network_type = self.get_network_type(message)
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle('drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint, token=auth_token)
            drf_network_id = message['Response']['network']['id']
            drf_network_name = message['Response']['network']['name']
            status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            while (status != 'active')  and (status != 'killed'):
                time.sleep(1)
                status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
                if status == 'active':
                    pdb.set_trace()
                    endpoint, auth_token = self.keystone_handle('drc', service_type='network', endpoint_type='publicURL')
                    drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                    network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                      'mtu':message['Response']['network']['mtu'],
                                      'name':"'_'.join([drf_network_name,'shadow'])",
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
        elif network_type == 'subnets':
            endpoint, auth_token = self.keystone_handle('drf', service_type='subnet', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint, token=auth_token)
            drf_subnet_id = message['Response']['subnet']['id']
            drf_subnet_name = message['Response']['subnet']['name']
            ##
            ## get the network status????????
            ##
            status = drf_neutron.list_subnets(name=drf_subnet_name)['subnets'][0]['status']
            while (status != 'active')  and (status != 'killed'):
                time.sleep(1)
                status = drf_neutron.list_subnets(name=drf_subnet_name)['subents'][0]['status']
                if status == 'active':
                    pdb.set_trace()
                    endpoint, auth_token = self.keystone_handle('drc', service_type='subnet', endpoint_type='publicURL')
                    drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                    subnet_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                      'mtu':message['Response']['network']['mtu'],
                                      'name':"'_'.join([drf_network_name,'shadow'])",
                                      'provider:network_type':message['Response']['network']['provider:network_type'],
                                      'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                      'router:external':message['Response']['network']['router:external'],
                                      'shared':message['Resopnse']['network']['shared'],
                                      'status':message['Resopnse']['network']['status'],
                                      'subnets':message['Response']['network']['subnets'],
                                      'tenant_id':message['Response']['network']['tenant_id']
                                      }
                    drc_neutron.create_subnet({'subnet':subnet_params})
                    subnets = drc_neutron.list_networks(name=network_params['name'])
                    drc_subnets_id = subnets['subnets'][0]['id']
                    # save <drf_subnet_id, drc_subnet_id, status> to DB



    def delete_handle(message):
        errlog = logging.getLogger("NeutronHandler:accept")
        neutronDao = DRNeutronDao(DRNeutron)
        network_type = self.get_netwrok_type()
        url = message['Request']['url'].split('/')
        network_primary_uuid = url[-1].split('.')[0]
        # get the secondary uuid from db for deleting network
        network_secondary_uuid = neutronDao.get_by_primary_uuid(network_primary_uuid).secondary_uuid
        if netwrok_secondary_uuid != None:
            endpoint, auth_token = self.keystone_handle('drc', service_type='network',endpoint_type='pyblicURL')
            drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
            if netwrok_type == 'networks':
                drc_neutron.delete_network(network_secondary_uuid)
               # delete one record from Neutron , but a alternative method is to set
               # a new deleted status
               #neutronDao.delete_by_primary_uuid(network_primary_uuid)
            elif network_type == 'subnets':
                pass


    def put_handle(message):
        endpoint, auth_token = self.keystone_handle("drf", service_type='network', endpoint_type='publicURL')
        drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
        drf_network_id = message['Response']['network']['id']
        drf_network_name = message['Response']['network']['name']
        status = drf__neutron.list_networks(name=drf_network_name)['networks'][0]['status']
        while (status != 'active') and (status != 'killed'):
            time.sleep(1)
            status = drf__neutron.list_networks(name=drf_network_name)['networks'][0]['status']
        if status == 'active':
            pdb.set_trace()
            endpoint, auth_token = self.keystone_handle("drf", service_type='network', endpoint_type='publicURL')
            drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
            # create


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
