import novaclient.v1_1.client as novaclient
from neutronclient.neutron import client as neutron_client
import keystoneclient.v2_0.client as keystoneclient
import argparse
import ConfigParser
#from  db_Dao import DRNeutronPortDao

def start_vm(instance_id):
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    drc_ncred={}
    drc_ncred['auth_url']= cf.get("drc","auth_url")
    drc_ncred['username']= cf.get("drc","user")
    drc_ncred['api_key'] = cf.get("drc","password")
    drc_ncred['project_id']=cf.get("drc","tenant_name")
    drc_nova = novaclient.Client(**drc_ncred)
    drc_nova.servers.start(instance_id)


def associate_floatingips(ports):
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
    for (port, floating_ip) in ports:
        print('--- ' + port + ' --- ' + floating_ip)
        drc_neutron.update_floatingip(floating_ip, {"port_id":port})


def start_vms(instance_ids):
    for instance_id in instance_ids:
        start_vm(instance_id)

def parse_arguments():
    ''' Parse arguments, we need the view, session id, and master_ip'''
    parser = argparse.ArgumentParser('arrakis_jobhandler.py')
    parser.add_argument('--instance_ids', dest='instance_id', type=str,
                        help='The instance ids will be started')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    instance_ids = args.instance_id.split(',')
    start_vms(instance_ids)
