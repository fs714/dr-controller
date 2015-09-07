import novaclient.v1_1.client as novaclient
from neutronclient.neutron import client as neutron_client
import keystoneclient.v2_0.client as keystoneclient
import argparse
import ConfigParser
#from  db_Dao import DRNeutronPortDao



'''
ports is a list ,[(secondary_port_uuid,secondary_floatingip_uuid),...]
you can get 'ports' by get_ports_associated() in DRNeutronPortDao.
'''
cf = ConfigParser.ConfigParser()
cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
keystone = keystoneclient.Client(auth_url=cf.get("drc","auth_url"),
                                 username=cf.get("drc","user"),
                                 password=cf.get("drc","password"),
                                 tenant_name=cf.get("drc","tenant_name"))
endpoint = keystone.service_catalog.url_for(service_type='network', endpoint_type='publicURL')
drc_neutron = neutron_client.Client('2.0', endpoint_url=endpoint, token=keystone.auth_token)
drc_neutron.update_floatingip("1414aaf4-4df7-4c09-8d7a-d6c218fdd275", {"floatingip":{"port_id":"29798f89-9074-48c6-af30-c5027a4535c3"}})


