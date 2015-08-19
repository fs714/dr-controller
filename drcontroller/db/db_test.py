#!/usr/bin/env python2.7
from db_Dao import DRGlanceDao, DRNovaDao, DRNeutronDao, DRNeutronSubnetDao
from models import Base, DRGlance, DRNova, DRNeutron, DRNeutronSubnet

def test_add():
    glanceDao = DRGlanceDao(DRGlance)
    print '<GlanceDao:add>: %s' % glanceDao.add(DRGlance(primary_uuid='primary_uuid_1',secondary_uuid='secondary_uuid_1',status='active_1',other='other_information'))
    print '<GlanceDao:add_mult>: %s' % glanceDao.add_mult([DRGlance(primary_uuid='primary_uuid_2',secondary_uuid='secondary_uuid_2',status='active_2',other='other_information'),\
                   DRGlance(primary_uuid='primary_uuid_3',secondary_uuid='secondary_uuid_3',status='active_3',other='other_information')])
    neutronDao = DRNeutronDao(DRNeutron)
    neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
    print '<NeutronDao:add>:%s' % neutronDao.add(DRNeutron(primary_uuid='primary_uuid_1',
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

def test_get():
    glanceDao = DRGlanceDao(DRGlance)
    neutronDao = DRNeutronDao(DRNeutron)
    neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
    print ' <GlanceDao:get>: %s' % glanceDao.get_by_primary_uuid('primary_uuid_1')
    print ' <GlanceDao:get_mult>: %s' % glanceDao.get_mult_by_primary_uuids(['primary_uuid_2','primary_uuid_3'])
    print '<GlnceDao:get_all>: %s' % glanceDao.get_all()
    print '<NeutronSubnetDao:get_subnets_by_network_id>:%s' % neutronSubnetDao.get_subnets_by_network_id('primary_uuid_1')
def test_delete():
    glanceDao = DRGlanceDao(DRGlance)
    neutronDao = DRNeutronDao(DRNeutron)
    neutronSubnetDao = DRNeutronSubnetDao(DRNeutronSubnet)
    print ' <GlanceDao:delete>: %s' % glanceDao.delete_by_primary_uuid('primary_uuid_1')
    print ' <GlanceDao:delete_mult>: %s' % glanceDao.delete_mult_by_primary_uuids(['primary_uuid_2','primary_uuid_3'])
    print '<GlnceDao:get_all>: %s' % glanceDao.get_all()
    print '<NeutronSubnetDao:delete_subnets>%s' % neutronSubnetDao.delete_subnets_by_network_id('secondary_uuid_1')

def test_update():
    glanceDao = DRGlanceDao(DRGlance)
    print ' <GlanceDao:update>: %s' % glanceDao.update_by_primary_uuid('primary_uuid_1', {'secondary_uuid':'secondary_uuid_1_update','status':'active_1_update'})

if __name__ == '__main__':
    test_add()
    #test_update()
    test_get()
    test_delete()
