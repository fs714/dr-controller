#!/usr/bin/env python2.7
from db_Dao import DRGlanceDao, DRNovaDao, DRNeutronNetDao, DRNeutronSubnetDao,DRNeutronPortDao, init_db, drop_db
from models import Base, DRGlance, DRNova, DRNeutronNet, DRNeutronSubnet, DRNeutronPort
def test_add():
    glanceDao = DRGlanceDao()
    neutronNetDao = DRNeutronNetDao()
    neutronSubnetDao = DRNeutronSubnetDao()
    novaDao = DRNovaDao()
    ##
    ## Glance
    ##
    print '<GlanceDao:add>: %s' % glanceDao.add(DRGlance(primary_uuid='primary_uuid_1',secondary_uuid='secondary_uuid_1',status='active_1',other='other_information'))
    print '<GlanceDao:add_mult>: %s' % glanceDao.add_mult([DRGlance(primary_uuid='primary_uuid_2',secondary_uuid='secondary_uuid_2',status='active_2',other='other_information'),\
                   DRGlance(primary_uuid='primary_uuid_3',secondary_uuid='secondary_uuid_3',status='active_3',other='other_information')])
    ##
    ## Neutron
    ##
    print '<NeutronDao:add>:%s' % neutronNetDao.add(DRNeutronNet(primary_uuid='primary_uuid_1',
                                                          secondary_uuid='secondary_uuid_1',
                                                          status='active_1',
                                                          deleted_flag='0',
                                                          other='other_information'))
    print '<NeutronSubnetDao:add>%s' % neutronSubnetDao.add(DRNeutronSubnet(primary_uuid='sub_primary_uuid_1',
                                                                            secondary_uuid='sub_secondary_uuid_1',
                                                                            status='active',
                                                                            deleted_flag='0',
                                                                            network_id='secondary_uuid_1',
                                                                            other='other_information'))
    print '<NeutronSubnetDao:add>%s' % neutronSubnetDao.add(DRNeutronSubnet(primary_uuid='sub_primary_uuid_2',
                                                                            secondary_uuid='sub_secondary_uuid_1',
                                                                            status='active',
                                                                            deleted_flag='0',
                                                                            network_id='secondary_uuid_1',
                                                                            other='other_information'))
    ##
    ## Nova
    ##
    print '<NovaDao:add>:%s' % novaDao.add(DRNova(primary_uuid='primary_uuid_1',
                                                  secondary_uuid='secondary_uuid_1',
                                                  node_name='node_name_1',
                                                  nova_type='0',
                                                  status='active',
                                                  other='other'))

    print '<NovaDao:add>:%s' % novaDao.add(DRNova(primary_uuid='primary_uuid_2',
                                                  secondary_uuid='secondary_uuid_2',
                                                  node_name='node_name_2',
                                                  nova_type='1',
                                                  status='active',
                                                  other='other'))
def test_get():
    glanceDao = DRGlanceDao()
    novaDao = DRNovaDao()
    #neutronNetDao = DRNeutronNetDao()
    neutronSubnetDao = DRNeutronSubnetDao()
    ##
    ## glance
    ##
    print ' <GlanceDao:get>: %s' % glanceDao.get_by_primary_uuid('primary_uuid_1')
    print ' <GlanceDao:get_mult>: %s' % glanceDao.get_mult_by_primary_uuids(['primary_uuid_2','primary_uuid_3'])
    print '<GlnceDao:get_all>: %s' % glanceDao.get_all()
    print '<GlnceDao:get_all_uuids>: %s' % glanceDao.get_all_uuids()
    ##
    ## neutron
    ##
    print '<NeutronSubnetDao:get_subnets_by_network_id>:%s' % neutronSubnetDao.get_subnets_by_network_id('primary_uuid_1')
    ##
    ## nova
    ##
    print '<NovaDao:get_all_uuids_node>: %s' % novaDao.get_all_uuids_node()
    print '<NovaDao:get_uuids_node>: %s' % novaDao.get_uuids_node(base=True)
    print '<NovaDao:get_uuids_node>: %s' % novaDao.get_uuids_node(False)

'''
def test_delete():
    glanceDao = DRGlanceDao()
    neutronNetDao = DRNeutronNetDao()
    neutronSubnetDao = DRNeutronSubnetDao()
    print ' <GlanceDao:delete>: %s' % glanceDao.delete_by_primary_uuid('primary_uuid_1')
    print ' <GlanceDao:delete_mult>: %s' % glanceDao.delete_mult_by_primary_uuids(['primary_uuid_2','primary_uuid_3'])
    print '<GlnceDao:get_all>: %s' % glanceDao.get_all()
    print '<NeutronSubnetDao:delete_subnets>%s' % neutronSubnetDao.delete_subnets_by_network_id('secondary_uuid_1')
'''

def test_update():
    glanceDao = DRGlanceDao()
    print ' <GlanceDao:update>: %s' % glanceDao.update_by_primary_uuid('primary_uuid_1', {'secondary_uuid':'secondary_uuid_1_update','status':'active_1_update'})

if __name__ == '__main__':
    init_db()
    test_add()
    #test_update()
    test_get()
    #test_delete()
    drop_db()
