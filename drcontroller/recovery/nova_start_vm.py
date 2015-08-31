import novaclient.v1_1.client as novaclient
import argparse
import ConfigParser

def start_vm(instance_id):
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/scripts/set.conf")
    drc_ncred={}
    drc_ncred['auth_url']= cf.get("drc","auth_url")
    drc_ncred['username']= cf.get("drc","user")
    drc_ncred['api_key'] = cf.get("drc","password")
    drc_ncred['project_id']=cf.get("drc","tenant_name")
    drc_nova = novaclient.Client(**drc_ncred)
    drc_nova.servers.start(instance_id)

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
