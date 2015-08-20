import logging
import string, os, sys, time
import pdb
from neutronclient.neutron import client as neutron_client
import base_handler
from db_Dao import DRNeutronDao, DRNeutronSubnetDao
from models import Base,DRNeutron, DRNeutronSubnet

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
        neutronDao = DRNeutronDao(DRNeutron)
        neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
        network_type = self.get_network_type(message)
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle('drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint, token=auth_token)
            drf_network_id = message['Response']['network']['id']
            drf_network_name = message['Response']['network']['name']
            ##
            ## Get the status of network looply, until it is 'active' or 'down'.
            ##
            status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            while (status != 'active')  and (status != 'down'):
                time.sleep(1)
                status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            ##
            ## network status is active, so create a shadow in secondary site.
            ##
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
                                    'subnets':message['Response']['network']['subnets']
                                    }
                drc_neutron.create_network({'network':network_params})
                networks = drc_neutron.list_networks(name=network_params['name'])
                drc_network_id = networks['networks'][0]['id']
                ##
                ## Add the mapping information : <drf_network_id, drc_network_id, status> to DB
                ##
                neutronDao.add(Neutron(primary_uuid=drf_network_id, secondary_uuid=drc_network_id, status=status, deleted_flag='0'))
        ##
        ## The request is for subnet
        ##
        elif network_type == 'subnets':
            endpoint, auth_token = self.keystone_handle('drf', service_type='subnet', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint, token=auth_token)
            drf_network_id = message['Request']['subnet']['netwrok_id']
            drf_subnet_id = message['Response']['subnet']['id']
            drf_subnet_name = message['Response']['subnet']['name']
            ##
            ## get the network status
            ##
            status = drf_neutron.list_subnets(name=drf_subnet_name)['subnets'][0]['status']
            while (status != 'active')  and (status != 'down'):
                time.sleep(1)
                status = drf_neutron.list_subnets(name=drf_subnet_name)['subents'][0]['status']
            ##
            ## the subnet status is active , so create a subnet shadow in secondary site.
            ##
            if status == 'active':
                pdb.set_trace()
                endpoint, auth_token = self.keystone_handle('drc', service_type='subnet', endpoint_type='publicURL')
                drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                # get the drc_network_id(secondary_uuid) of secondary site from DB.
                drc_network_id = neutronDao.get_primary_uuid(primary_uuid=drf_network_id).secondary_uuid
                subnet_params = {'allocation_pools':{'start':message['Response']['subnet']['allocation_pools']['start'],
                                                      'end':message['Response']['subnet']['allocation_pools']['end']},
                                 'cidr':message['Response']['subnet']['cidr'],
                                 'dns_nameservers':message['Response']['subnet']['dns_nameservers'],
                                 'enable_dhcp':message['Response']['subnet']['enable_dhcp'],
                                 'gateway_ip':message['Response']['subnet']['gateway_ip'],
                                 'host_routes':message['Response']['subnet']['host_routes'],
                                 'ip_version':message['Resopnse']['subnet']['ip_version'],
                                 'ipv6_address_mode':message['Resopnse']['subnet']['ipv6_address_mode'],
                                 'ipv6_ra_mode':message['Response']['subnet']['ipv6_ra_mode'],
                                 'name':"'_'.join([drf_subnet_name,'shadow'])",
                                 'network_id':str(drc_network_id),
                                 'subnetpool_id':message['Response']['subnet']['subnetpool_id']
                                 }
                drc_neutron.create_subnet({'subnet':subnet_params})
                subnets = drc_neutron.list_subnets(name=network_params['name'])
                drc_subnets_id = subnets['subnets'][0]['id']
                ##
                ## save the subnet mapping  information:<network_id, primary_uuid, secondary_uuid, status> to NeutronSubnet
                ##
                neutronSubnetDao.add(NeutronSubnet(network_id=drc_network_id,
                                                    primary_uuid=drf_subnet_uuid,
                                                    secondary_uuid=drc_subnet_id,
                                                    status=status,
                                                    deleted_flag='0',
                                                    other='other'))

    def delete_handle(message):
        errlog = logging.getLogger("NeutronHandler:accept")
        neutronDao = DRNeutronDao(DRNeutron)
        neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
        network_type = self.get_netwrok_type()
        ##
        ## The request is for network.
        ##
        if netwrok_type == 'networks':
            url = message['Request']['url'].split('/')
            network_primary_uuid = url[-1].split('.')[0]
            ## get the secondary uuid from db for deleting network
            network_secondary_uuid = neutronDao.get_by_primary_uuid(network_primary_uuid).secondary_uuid
            if netwrok_secondary_uuid != None:
                endpoint, auth_token = self.keystone_handle('drc', service_type='network',endpoint_type='pyblicURL')
                drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                drc_neutron.delete_network(network_secondary_uuid)
                ## delete network means that all subnets of it alse must be deleted.
                neutronDao.delete_by_primary_uuid(network_primary_uuid)
                neutronSubnetDao.delete_subnets_by_network_id(network_secondary_uuid)
        ##
        ## The request is for subnet.
        ##
        elif network_type == 'subnets':
            url = message['Request']['url'].split('/')
            subnet_primary_uuid = url[-1].split('.')[0]
            subnet_secondary_uuid = neutronSubnetDao.get_by_primary_uuid(subnet_primary_uuid).secondary_uuid
            endpoint, auth_token = self.keystone_handle('drc', service_type='subnet',endpoint_type='pyblicURL')
            drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
            drc_neutron.delete_subnet(subnet_secondary_uuid)
            ##
            ## delete this subnet from table dr_neutron_subnet
            ##
            neutronSubnetDao.delete_by_primary_uuid(subnet_primary_uuid)


    def put_handle(message):
        neutronDao = DRNeutronDao(DRNeutron)
        neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
        network_type = self.get_netwrok_type()
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle("drf", service_type='network', endpoint_type='publicURL')
            drf_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
            url = message['Request']['url'].split('/')
            drf_netwrok_uuid = url[-1].split('.')[0]
            drf_network_name = message['Response']['network']['name']
            ##
            ## get the network status.
            ## regardless of 'BUILD' status.
            status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            while (status != 'active') and (status != 'down'):
                time.sleep(1)
                status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            ##
            ## the network status is active , so update the network shadow in secondary site.
            ##
            if status == 'active':
                pdb.set_trace()
                endpoint, auth_token = self.keystone_handle("drf", service_type='network', endpoint_type='publicURL')
                drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                # get drc_network_uuid of  secondary site  from DB
                drc_network_uuid=neutronDao.get_by_primary_uuid(drf_network_uuid).secondary_uuid
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                    'mtu':message['Response']['network']['mtu'],
                                    'name':"'_'.join([drf_network_name,'shadow'])",
                                    'provider:network_type':message['Response']['network']['provider:network_type'],
                                    'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                    'router:external':message['Response']['network']['router:external'],
                                    'shared':message['Resopnse']['network']['shared'],
                                    'status':message['Resopnse']['network']['status'],
                                    'subnets':message['Response']['network']['subnets'],
                                    'id':str(drc_network_uuid)
                                    }
                drc_neutron.update_network({'network':network_params})
            ##
            ## the network status is down, so update status of the network-shadow to 'down' in secondary site.
            ##
            elif status == 'down':
                # set the status of netwrok is 'down' in DB
                neutronDao.update_by_primary_uuid(drf_network_uuid, {'status':'down'})
                # How to deal with subnets when their network is down
        ##
        ## The request is for subnet.
        ##
        elif netwrok_type == 'subnets':
            endpoint, auth_token = self.keystone_handle("drf", service_type='subnet', endpoint_type='publicURL')
            drf_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
            url = message['Request']['url'].split('/')
            drf_subnet_uuid = url[-1].split('.')[0]
            drf_network_id = message['Request']['subnet']['netwrok_id']
            drf_subnet_name = message['Response']['subnet']['name']
            ##
            ## get the subnet status.
            ##
            status = drf_neutron.list_subnets(name=drf_subnet_name)['subnets'][0]['status']
            while (status != 'active')  and (status != 'down'):
                time.sleep(1)
                status = drf_neutron.list_subnets(name=drf_subnet_name)['subents'][0]['status']
            ##
            ## the subnet status is active , so update the  subnet shadow in secondary site.
            ##
            if status == 'active':
                pdb.set_trace()
                endpoint, auth_token = self.keystone_handle('drc', service_type='subnet', endpoint_type='publicURL')
                drc_neutron = neutronclient.Client('2.0', endpoint, token=auth_token)
                ##
                ## get drc_network_id(secondary_uuid) and drc_subnet_uuid of secondary site from DB.
                ##
                drc_network_id = neutronDao.get_primary_uuid(primary_uuid=drf_network_id).secondary_uuid
                drc_subnet_uuid = neutronSubnetDao.get_primary_uuid(primary_uuid=drf_subnet_uuid).secondary_uuid
                subnet_params = {'id':drc_subnet_uuid,
                                 'allocation_pools':{'start':message['Response']['subnet']['start'],
                                                     'end': message['Response']['subnet']['end']},
                                 'cidr':message['Response']['subnet']['cidr'],
                                 'dns_nameservers':message['Response']['subnet']['dns_nameservers'],
                                 'enable_dhcp':message['Response']['subnet']['enable_dhcp'],
                                 'gateway_ip':message['Response']['subnet']['gateway_ip'],
                                 'host_routes':message['Response']['subnet']['host_routes'],
                                 'ip_version':message['Resopnse']['subnet']['ip_version'],
                                 'ipv6_address_mode':message['Resopnse']['subnet']['ipv6_address_mode'],
                                 'ipv6_ra_mode':message['Response']['subnet']['ipv6_ra_mode'],
                                 'name':"'_'.join([drf_subnet_name,'shadow'])",
                                 'network_id':str(drc_network_id),
                                 'subnetpool_id':message['Response']['subnet']['subnetpool_id']
                                 }
                # update the subnet-shadow
                drc_neutron.update_subnet({'subnet':subnet_params})
            ##
            ## the subnet status is down, so update the subnet-shadow status to down.
            ##
            if status == 'down':
                neutronSubnetDao.update_by_primary_uuid(drf_subnet_uuid,{'status':status})
        ##
        ## request for port.
        ##
        else:
            print 'NeutronAPP put_handle is Error.'
            return



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
