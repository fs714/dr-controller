import novaclient.v1_1.client as novaclient
import ConfigParser

def start_vm(server_id):
    cf=ConfigParser.ConfigParser()
    cf.read("/home/eshufan/projects/drcontroller/drcontroller/conf/set.conf")
    drc_ncred={}
    drc_ncred['auth_url']= cf.get("drc","auth_url")
    drc_ncred['username']= cf.get("drc","user")
    drc_ncred['api_key'] = cf.get("drc","password")
    drc_ncred['project_id']=cf.get("drc","tenant_name")
    drc_nova = novaclient.Client(**drc_ncred)
    drc_nova.servers.start(server_id)

