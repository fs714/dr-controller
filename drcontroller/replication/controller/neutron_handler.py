import logging
import string, os, sys, time
import pdb
import ConfigParser
from neutronclient.neutron import client as neutron_client
import base_handler
from db.db_Dao import DRNeutronNetDao, DRNeutronSubnetDao ,DRNeutronPortDao, DRNeutronRouterDao
from db.models import Base,DRNeutronNet, DRNeutronSubnet, DRNeutronPort, DRNeutronRouter

set_conf = "/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf"
handle_type = "Neutron"

class NeutronApp(base_handler.BaseHandler):

    def __init__(self, set_conf, handle_type):
        super(NeutronApp, self).__init__(set_conf)
        self.handle_type = handle_type
        self.logger = logging.getLogger("NeutronHandler")

    def get_network_type(self, message):
        '''
        Get the network type for 'networks' , 'subnets' or 'routers'.
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
            network_type= url[4]
            return network_type
        else:
            return 'error_network_type'

    def post_handle(self, message):
        '''
        Create a network, subnet or  router.
        '''
        neutronNetDao = DRNeutronNetDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        neutronRouterDao = DRNeutronRouterDao()
        #network_type = self.get_network_type(message)
        network_type = message['Request']['url'].split('/')[4].split('.')[0]
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle(key_type='drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0',endpoint_url=endpoint, token=auth_token)
            drf_network_id = message['Response']['network']['id']
            drf_network_name = message['Response']['network']['name']
            self.logger.info('Create shadow network for '+ drf_network_id + ' in dr site')
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
            #    pdb.set_trace()
                auth_endpoint_url, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0',endpoint_url=auth_endpoint_url, token=auth_token)
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                    'name':'_'.join([drf_network_name,'shadow']),
                                    'provider:network_type':message['Response']['network']['provider:network_type'],
                                    #'provider:physical_network':message['Response']['network']['provider:physical_network'],
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
                neutronNetDao.add(DRNeutronNet(primary_uuid=drf_network_id, secondary_uuid=drc_network_id, status=status, deleted_flag='0'))
                self.logger.info('Shadow network ' + drc_network_id + ' created for '+ drf_network_id + ' in dr site')
        ##
        ## The request is for subnet
        ##
        elif network_type == 'subnets':
            #pdb.set_trace()
            endpoint, auth_token = self.keystone_handle(key_type='drf', service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            drf_network_id = message['Response']['subnet']['network_id']
            drf_subnet_id = message['Response']['subnet']['id']
            drf_subnet_name = message['Response']['subnet']['name']
            self.logger.info('Create shadow subnet for '+ drf_subnet_id + ' in dr site')
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            # get the drc_network_id(secondary_uuid) of secondary site from DB
            count = 0
            drc_network_id = None
            neutron_network = neutronNetDao.get_by_primary_uuid(primary_uuid=drf_network_id)
            while neutron_network == None:
                time.sleep(1)
                neutron_network = neutronNetDao.get_by_primary_uuid(primary_uuid=drf_network_id)
                if neutron_network != None:
                    drc_network_id = neutron_network.secondary_uuid
                    break
                else:
                    count=count+1
                if count == 5:
                    break
            if drc_network_id == None:
                print 'Create subnet Error: can not find network in DB'
                return
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
            self.logger.info('Shadow subnet ' + drc_subnet_id + ' created for '+ drf_subnet_id + ' in dr site')
        elif network_type == 'routers':
            #pdb.set_trace()
            drf_router_name = message['Response']['router']['name']
            drf_router_id=message['Response']['router']['id']
            drf_router_admin_state_up=message['Response']['router']['admin_state_up']
            set_external_gateway=False
            drf_external_gateway_info=message['Response']['router']['external_gateway_info']
            if drf_external_gateway_info!=None:
                set_external_gateway=True
            self.logger.info('Create shadow router for ' + drf_router_id + ' in dr site')
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            router_params={'name':'_'.join([drf_router_name,'shadow']),
                           'admin_state_up':drf_router_admin_state_up,
                           'external_gateway_info':None}
            drc_neutron.create_router({'router':router_params})
            routers = drc_neutron.list_routers(name=router_params['name'])
            drc_router_id = routers['routers'][0]['id']
            if set_external_gateway:
                drc_ext_net_id ='be7953ea-b9c5-4a74-962f-a367f9aa0743'
                drc_neutron.add_gateway_router(drc_router_id,{'network_id':drc_ext_net_id})
            neutronRouterDao.add(DRNeutronRouter(primary_uuid=drf_router_id,
                                          secondary_uuid=drc_router_id,
                                          other='other'))
            self.logger.info('Shadow router ' + drc_router_id + ' created for '+ drf_router_id + ' in dr site')


        else:
            print'Error:NeutronHandle ->post_handle : unknow handle type'
            return

    def delete_handle(self,message):
        neutronNetDao = DRNeutronNetDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        neutronRouterDao = DRNeutronRouterDao()
        #network_type = self.get_network_type(message)
        url= message['Request']['url'].split('/')
        network_type = url[4]
        uuid = url[5].split('.')[0]
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            #pdb.set_trace()
            #url = message['Request']['url'].split('/')
            #network_primary_uuid = url[-1].split('.')[0]
            network_primary_uuid = uuid
            ## get the secondary uuid from db for deleting network
            network_secondary_uuid = neutronNetDao.get_by_primary_uuid(network_primary_uuid).secondary_uuid
            if network_secondary_uuid != None:
                endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network',endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                ## delete network means that all subnets of it alse must be deleted.
                drc_neutron.delete_network(network_secondary_uuid)
                neutronSubnets = neutronSubnetDao.get_subnets_by_network_id(network_secondary_uuid)
                neutronNetDao.delete_by_primary_uuid(network_primary_uuid)
                neutronSubnetDao.delete_subnets_by_network_id(network_secondary_uuid)
                self.logger.info('Delete shadow network ' + network_secondary_uuid + ' for ' + network_primary_uuid + ' in dr site')
        ##
        ## The request is for subnet.
        ##
        elif network_type == 'subnets':
           # pdb.set_trace()
            #url = message['Request']['url'].split('/')
            #subnet_primary_uuid = url[-1].split('.')[0]
            subnet_primary_uuid = uuid
            subnet_secondary_uuid = neutronSubnetDao.get_by_primary_uuid(subnet_primary_uuid).secondary_uuid
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network',endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            drc_neutron.delete_subnet(subnet_secondary_uuid)
            ##
            ## delete this subnet from table dr_neutron_subnet
            ##
            neutronSubnetDao.delete_by_primary_uuid(subnet_primary_uuid)
            self.logger.info('Delete shadow subnet ' + subnet_secondary_uuid + ' for ' + subnet_primary_uuid + ' in dr site')
        elif network_type == 'routers':
            #pdb.set_trace()
            drf_router_uuid = uuid
            ##
            ## get secondary uuid from DB
            ##
            drc_router_uuid = neutronRouterDao.get_by_primary_uuid(drf_router_uuid).secondary_uuid
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)

            ##
            ## delete router uuid maping from DB
            ##
            drc_neutron.delete_router(drc_router_uuid)
            neutronRouterDao.delete_by_primary_uuid(drf_router_uuid)
            self.logger.info('Delete shadow router ' + drc_router_uuid + ' for ' + drf_router_uuid + ' in dr site')

        else:
            print 'ERROR:Neutron_handle delete_handle unknown handle type.'
            return


    def put_handle(self, message):
        neutronNetDao = DRNeutronNetDao()
        neutronSubnetDao = DRNeutronSubnetDao()
        neutronPortDao = DRNeutronPortDao()
        neutronRouterDao = DRNeutronRouterDao()
        #network_type = self.get_network_type(message)
        url= message['Request']['url'].split('/')
        network_type = url[4]
        uuid = url[5].split('.')[0]
        ##
        ## The request is for network.
        ##
        if network_type == 'networks':
            endpoint, auth_token = self.keystone_handle(key_type="drf", service_type='network', endpoint_type='publicURL')
            drf_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            #url = message['Request']['url'].split('/')
            drf_network_uuid = uuid
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
            #    pdb.set_trace()
                endpoint, auth_token = self.keystone_handle(key_type="drc", service_type='network', endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                # get drc_network_uuid of  secondary site  from DB
                drc_network_uuid=neutronNetDao.get_by_primary_uuid(drf_network_uuid).secondary_uuid
                network_params = {'admin_state_up':message['Response']['network']['admin_state_up'],
                                    'name':'_'.join([drf_network_name,'shadow']),
                                    #'provider:network_type':message['Response']['network']['provider:network_type'],
                                    # 'provider:physical_network':message['Response']['network']['provider:physical_network'],
                                    #'provider:segmentation_id': message['Response']['network']['provider:segmentation_id'],
                                    'router:external':message['Response']['network']['router:external'],
                                    'shared':message['Response']['network']['shared'],
                                 }

                drc_neutron.update_network(drc_network_uuid,{'network': network_params})
                self.logger.info('Update network ' + drc_network_uuid + ' in dr site according to ' + drf_network_uuid)
            ##
            ## the network status is down, so update status of the network-shadow to 'down' in secondary site.
            ##
            elif status == 'DOWN':
                # set the status of netwrok is 'down' in DB
                neutronNetDao.update_by_primary_uuid(drf_network_uuid, {'status':'DOWN'})
        ##
        ## The request is for subnet.
        ##
        elif network_type == 'subnets':
            drf_subnet_uuid = uuid
            drf_subnet_name = message['Response']['subnet']['name']
            #pdb.set_trace()
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
            self.logger.info('Update subnet ' + drc_subnet_uuid + ' in dr site according to ' + drf_subnet_uuid)
        elif network_type == 'routers':
            #pdb.set_trace()
            url = message['Request']['url'].split('/')
            # ROUTER:router-interface-add/remove
            if len(url)==7:
                interface_handle_type = url[-1].split('.')[0]
                drf_router_id = message['Response']['id']
                #drf_router_id = '79811a02-05a1-4df3-b62e-df88a271cd01'
                drf_subnet_id = message['Response']['subnet_id']
                #
                # get subnet_id(subnet_ids) from DB
                #
                drc_subnet_id = neutronSubnetDao.get_by_primary_uuid(drf_subnet_id).secondary_uuid
                #drc_router_id = '35735fea-2971-47a4-b8e4-a8f65d3bea98'
                drc_router_id = neutronRouterDao.get_by_primary_uuid(drf_router_id).secondary_uuid
                endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
                drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                #
                # only one subnet be handle
                #
                if interface_handle_type == 'add_router_interface':
                    drc_neutron.add_interface_router(drc_router_id,{'subnet_id':drc_subnet_id})
                    self.logger.info('Add subnet ' + drc_subnet_id + ' to router ' + drc_router_id + ' in dr site according to ' + drf_router_id)
                elif interface_handle_type =='remove_router_interface':
                    drc_neutron.remove_interface_router(drc_router_id, {'subnet_id':drc_subnet_id})
                    self.logger.info('Remove subnet ' + drc_subnet_id + ' from router ' + drc_router_id + ' in dr site according to ' + drf_router_id)
            # ROUTER:gateway-set /gateway-clear ,router-update
            elif len(url)==6:
                is_router_update=False
                drf_router_id = message['Response']['router']['id']
                ##
                ## get secondary site router uuid from DB
                ##
                drc_router_id = neutronRouterDao.get_by_primary_uuid(drf_router_id).secondary_uuid
                if message['Request']['wsgi.input']['router'].has_key('name'):
                    is_router_update=True
                    drf_router_name=message['Request']['wsgi.input']['router']['name']
                    drf_router_admin_state_up=message['Request']['wsgi.input']['router']['admin_state_up']
                if is_router_update:
                    endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
                    drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                    router_params={'admin_state_up': drf_router_admin_state_up,
                                    'name':'_'.join([drf_router_name,'shadow'])}
                    drc_neutron.update_router(drc_router_id,{'router':router_params})

                else:
                    drf_external_gateway_info=message['Response']['router']['external_gateway_info']
                    if drf_external_gateway_info==None:
                        gateway_handle_type='gateway-clear'
                    else:
                        gateway_handle_type='gateway-set'
                        drf_ext_net_id='4480e49d-92d0-4686-b6c5-20ca8d2d7e45'
                        #drf_ext_net_id =message['Response']['router']['external_gateway_info']['network_id']
                        drc_ext_net_id ='be7953ea-b9c5-4a74-962f-a367f9aa0743'
                        endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
                        drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
                        if gateway_handle_type=='gateway-set':
                            drc_neutron.add_gateway_router(drc_router_id,{'network_id':drc_ext_net_id})
                            self.logger.info('Set gateway for router ' + drc_router_id + ' in dr site according to ' + drf_router_id)
                        elif gateway_handle_type=='gateway-clear':
                            drc_neutron.remove_gateway_router(drc_router_id)
                            self.logger.info('Clear gateway for router ' + drc_router_id + ' in dr site according to ' + drf_router_id)
            else:
                print 'ERROR:PUT->Router:unknown handle type of router.'
                return
        elif network_type == 'floatingips':
            #pdb.set_trace()
            # judge the handle type by fixed_ip_address is 'None' or not .
            fixed_ip_address = message['Response']['floatingip']['fixed_ip_address']
            if fixed_ip_address!=None:
                floatingip_handle_type='associate'
            else:
                floatingip_handle_type='disassociate'
            drf_floating_ip_address = message['Response']['floatingip']['floating_ip_address']
            drc_floating_ip_address = drf_floating_ip_address
            drf_floatingip_id = message['Response']['floatingip']['id']
            drf_port_id = message['Response']['floatingip']['port_id']
            endpoint, auth_token = self.keystone_handle(key_type='drc', service_type='network', endpoint_type='publicURL')
            drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=auth_token)
            if floatingip_handle_type == 'associate':
                drc_floatingips = drc_neutron.list_floatingips()['floatingips']
                for fip in drc_floatingips:
                    if fip['floating_ip_address'] == drf_floating_ip_address:
                        drc_floatingip_id = fip['id']
                #
                # get the secondary port information from DB
                #
                try:
                    drc_port_id = neutronPortDao.get_by_primary_uuid(primary_uuid=drf_port_id).secondary_uuid
                except:
                    print'Neutron no get "drc_port_id from DB"'
                    return
                #drc_neutron.update_floatingip(drc_floatingip_id,{"floatingip":{"port_id":drc_port_id}})
                #
                # update the DB , primary_floatingip_uuid,secondary_floatingip_uuid,floating_ip_address
                #
                neutronPortDao.update_by_primary_uuid(drf_port_id,{'primary_floatingip_uuid':drf_floatingip_id,
                                                                   'secondary_floatingip_uuid':drc_floatingip_id,
                                                                   'primary_floating_ip_address':drf_floating_ip_address,
                                                                   'secondary_floating_ip_address':drc_floating_ip_address})
                self.logger.info('Record floating IP information in database: ' + drf_floating_ip_address + ' : ' + drc_floating_ip_address)
            elif floatingip_handle_type == 'disassociate':
                #pdb.set_trace()
                try:
                    drf_port_id = neutronPortDao.get_port_by_primary_floatingip_uuid(drf_floatingip_id).primary_uuid
                except:
                    print 'floatingip-disassociate:no get drf_port_id'
                    return
                #drc_neutron.update_floatingip(drc_floatingip_id)
                neutronPortDao.update_by_primary_uuid(drf_port_id,{'primary_floatingip_uuid':None,'secondary_floatingip_uuid':None,'primary_floating_ip_address':None,'secondary_floating_ip_address':None})
                self.logger.info('Remove floating IP information in database: ' + drf_port_id)
        else:
            print 'NeutronAPP put_handle is Error.'
            return



class NeutronHandler(object):
    def __init__(self):
        self.neutron_app = NeutronApp(set_conf, handle_type)
        self.logger = logging.getLogger("NeutronHandler")

    def accept(self, *req, **kwargs):
        self.logger.info("Neutron request accept")
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
        return ['Hello Neutron']
