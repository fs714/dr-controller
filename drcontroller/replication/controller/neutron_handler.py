import logging
import string, os, sys, time
import pdb
from neutronclient.neutron import client as neutron_client
import base_handler
from db_Dao import DRNeutronDao, DRNeutronSubnetDao
from models import Base,DRNeutron, DRNeutronSubnet
#set_conf = "/home/eshufan/project/drcontroller/drcontroller/conf/set.conf"
set_conf = "/home/eshufan/project/drcontroller/drcontroller/replication/controller/set.conf"
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
        neutronDao = DRNeutronDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        network_type = self.get_network_type(message)
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle(key_type='drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0',endpoint_url=endpoint, token=auth_token)
            drf_network_id = message['Response']['network']['id']
            drf_network_name = message['Response']['network']['name']
            ##
            ## Get the status of network looply, until it is 'active' or 'down'.
            ##
            networks =drf_neutron.list_networks(name=drf_network_name)
            status = networks['networks'][0]['status']
            while (status != 'ACTIVE')  and (status != 'DOWN') and (status != 'ERROR'):
                time.sleep(1)
                status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            ##
            ## network status is active, so create a shadow in secondary site.
            ##
            if status == 'ACTIVE':
                pdb.set_trace()
                auth_endpoint_url, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0',endpoint_url=auth_endpoint_url, token=auth_token)
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                    'name':'_'.join([drf_network_name,'shadow']),
                                    'provider:network_type':message['Response']['network']['provider:network_type'],
                                   # 'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                    #'provider:segmentation_id': message['Response']['network']['provider:segmentation_id'],
                                    'router:external':message['Response']['network']['router:external'],
                                    'shared':message['Response']['network']['shared']
                                    }
                drc_neutron.create_network({'network':network_params})
                networks = drc_neutron.list_networks(name=network_params['name'])
                drc_network_id = networks['networks'][0]['id']
                ##
                ## Add the mapping information : <drf_network_id, drc_network_id, status> to DB
                ##
                neutronDao.add(DRNeutron(primary_uuid=drf_network_id, secondary_uuid=drc_network_id, status=status, deleted_flag='0'))
        ##
        ## The request is for subnet
        ##
        elif network_type == 'subnets':
            pdb.set_trace()
            endpoint, auth_token = self.keystone_handle(key_type='drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            drf_network_id = message['Response']['subnet']['network_id']
            drf_subnet_id = message['Response']['subnet']['id']
            drf_subnet_name = message['Response']['subnet']['name']
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            # get the drc_network_id(secondary_uuid) of secondary site from DB.
            drc_network_id = neutronDao.get_by_primary_uuid(primary_uuid=drf_network_id).secondary_uuid
            subnet_params ={ 'allocation_pools':message['Response']['subnet']['allocation_pools'],
                             'cidr':message['Response']['subnet']['cidr'],
                             'dns_nameservers':message['Response']['subnet']['dns_nameservers'],
                             'enable_dhcp':message['Response']['subnet']['enable_dhcp'],
                             'gateway_ip':message['Response']['subnet']['gateway_ip'],
                             'host_routes':message['Response']['subnet']['host_routes'],
                             'ip_version':message['Response']['subnet']['ip_version'],
                             'name':'_'.join([drf_subnet_name,'shadow']),
                             'network_id':str(drc_network_id),
                             'subnetpool_id':message['Response']['subnet']['subnetpool_id']
                             }
            drc_neutron.create_subnet({'subnet':subnet_params})
            subnets = drc_neutron.list_subnets(name=subnet_params['name'])
            drc_subnet_id = subnets['subnets'][0]['id']
            ##
            ## save the subnet mapping  information:<network_id, primary_uuid, secondary_uuid, status> to NeutronSubnet
            ##
            neutronSubnetDao.add(DRNeutronSubnet(network_id=drc_network_id,
                                                 primary_uuid=drf_subnet_id,
                                                 secondary_uuid=drc_subnet_id,
                                                 deleted_flag='0',
                                                 other='other'))

    def delete_handle(self,message):
        errlog = logging.getLogger("NeutronHandler:accept")
        neutronDao = DRNeutronDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        network_type = self.get_network_type(message)
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            pdb.set_trace()
            url = message['Request']['url'].split('/')
            network_primary_uuid = url[-1].split('.')[0]
            ## get the secondary uuid from db for deleting network
            network_secondary_uuid = neutronDao.get_by_primary_uuid(network_primary_uuid).secondary_uuid
            if network_secondary_uuid != None:
                endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network',endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                ## delete network means that all subnets of it alse must be deleted.
                drc_neutron.delete_network(network_secondary_uuid)
                neutronSubnets = neutronSubnetDao.get_subnets_by_network_id(network_secondary_uuid)
                for delete_subnet in neutronSubnets:
                    drc_neutron.delete_subnet(delete_subnet.secondary_uuid)
                neutronDao.delete_by_primary_uuid(network_primary_uuid)
                neutronSubnetDao.delete_subnets_by_network_id(network_secondary_uuid)
        ##
        ## The request is for subnet.
        ##
        elif network_type == 'subnets':
            pdb.set_trace()
            url = message['Request']['url'].split('/')
            subnet_primary_uuid = url[-1].split('.')[0]
            subnet_secondary_uuid = neutronSubnetDao.get_by_primary_uuid(subnet_primary_uuid).secondary_uuid
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network',endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            drc_neutron.delete_subnet(subnet_secondary_uuid)
            ##
            ## delete this subnet from table dr_neutron_subnet
            ##
            neutronSubnetDao.delete_by_primary_uuid(subnet_primary_uuid)


    def put_handle(self, message):
        neutronDao = DRNeutronDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        network_type = self.get_network_type(message)
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle(key_type="drf", service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            url = message['Request']['url'].split('/')
            drf_network_uuid = url[-1].split('.')[0]
            drf_network_name = message['Response']['network']['name']
            ##
            ## get the network status.
            ## regardless of 'BUILD' status.
            status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            while (status != 'ACTIVE') and (status != 'DOWN') and (status != 'ERROR'):
                time.sleep(1)
                status = drf_neutron.list_networks(name=drf_network_name)['networks'][0]['status']
            ##
            ## the network status is active , so update the network shadow in secondary site.
            ##
            if status == 'ACTIVE':
                pdb.set_trace()
                endpoint, auth_token = self.keystone_handle(key_type="drf", service_type='network', endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                # get drc_network_uuid of  secondary site  from DB
                drc_network_uuid=neutronDao.get_by_primary_uuid(drf_network_uuid).secondary_uuid
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                    'name':'_'.join([drf_network_name,'shadow']),
                                    #'provider:network_type':message['Response']['network']['provider:network_type'],
                                    # 'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                    #'provider:segmentation_id': message['Response']['network']['provider:segmentation_id'],
                                    'router:external':message['Response']['network']['router:external'],
                                    'shared':message['Response']['network']['shared'],
                                 }

                drc_neutron.update_network(drc_network_uuid,{'network': network_params})
            ##
            ## the network status is down, so update status of the network-shadow to 'down' in secondary site.
            ##
            elif status == 'DOWN':
                # set the status of netwrok is 'down' in DB
                neutronDao.update_by_primary_uuid(drf_network_uuid, {'status':'DOWN'})
        ##
        ## The request is for subnet.
        ##
        elif network_type == 'subnets':
            endpoint, auth_token = self.keystone_handle(key_type="drf", service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            url = message['Request']['url'].split('/')
            drf_subnet_uuid = url[-1].split('.')[0]
            drf_subnet_name = message['Response']['subnet']['name']
            ##
            ## the subnet status is active , so update the  subnet shadow in secondary site.
            ##
            pdb.set_trace()
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            ##
            ## get drc_network_id(secondary_uuid) and drc_subnet_uuid of secondary site from DB.
            ##
            drc_subnet_uuid = neutronSubnetDao.get_by_primary_uuid(primary_uuid=drf_subnet_uuid).secondary_uuid
            subnet_params = {'allocation_pools':message['Response']['subnet']['allocation_pools'],
                             'dns_nameservers':message['Response']['subnet']['dns_nameservers'],
                             'enable_dhcp':message['Response']['subnet']['enable_dhcp'],
                             'gateway_ip':message['Response']['subnet']['gateway_ip'],
                             'host_routes':message['Response']['subnet']['host_routes'],
                              #destination (Optional)
                              #nexthop (Optional)
                             'name':'_'.join([drf_subnet_name,'shadow'])
                             }
            # update the subnet-shadow
            drc_neutron.update_subnet(drc_subnet_uuid, {'subnet':subnet_params})
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
                        self.neutron_app.post_handle(message)
                        print 'post'
                     elif message['Request']['type'] == 'DELETE':
                        self.neutron_app.delete_handle(message)
                        print 'delete'
                     elif message['Request']['type'] == 'PUT':
                        self.neutron_app.put_handle(message)
                        print 'put'
        self.logger.info("--- Hello Neutron ---")
        return ['Hello Neutron']
