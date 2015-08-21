#!/usr/bin/env python2.7
import sys
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base

sys.path.append('/home/eshufan/project/drcontroller/drcontroller/db')

Base = declarative_base()

def init_db():
    Base.metadata.create_all(engine)

def drop_db():
    Base.metadata.drop_all(engine)
'''
Models for DRGlance, DRNeutron, DRNova
'''
class DRGlance(Base):
    '''
    Model class DRGlance
    '''
    __tablename__ = "dr_glance"

    id = Column(Integer, Sequence('dr_glance_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    status = Column(String(20))
    other = Column(String(50))

    def __repr__(self):
        return "<DRGlance(primary_uuid = '%s', secondary_uuid = '%s', status = '%s', other = '%s')>" % (self.primary_uuid, self.secondary_uuid, self.status, self.other)


class DRNeutron(Base):
    '''
    Model class DRNeutron
    '''
    __tablename__ = "dr_neutron"

    id = Column(Integer, Sequence('dr_neutron_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    forward = Column(String(255))
    request = Column(String(255))
    status = Column(String(20))
    deleted_flag = Column(String(2))
    other =  Column(String(50))

    def __repr__(self):
        return "<DRNeutron(primary_uuid = '%s', secondary_uuid = '%s', forward = '%s', request='%s', status = '%s', deleted_flag = '%s', other = '%s')>" %\
                (self.primary_uuid, self.secondary_uuid, self.forward, self.request, self.status, self.deleted_flag, self.other)

class DRNeutronSubnet(Base):
    '''
    Model class DRNeutron
    '''
    __tablename__ = "dr_neutron_subnet"

    id = Column(Integer, Sequence('dr_neutron_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    status = Column(String(20))
    deleted_flag = Column(String(2))
    # network_id  relate to DRNeutron.secondary_uuid
    network_id = Column(String(50))
    other =  Column(String(50))

    def __repr__(self):
        return "<DRNeutronSubnet(network_id = %s, primary_uuid = '%s', secondary_uuid = '%s', status = '%s',deleted_flag = '%s', other = '%s')>" %\
                (self.network_id, self.primary_uuid, self.secondary_uuid, self.status, self.deleted_flag, self.other)

class DRNova(Base):
    '''
    Model Class DRNova
    '''
    __tablename__ = "dr_nova"

    id = Column(Integer, Sequence('dr_nova_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    node_name = Column(String(50))
    status = Column(String(20))
    # 0:base, 1:runtime
    nova_type = Column(String(2))
    other = Column(String(50))

    def __repr__(self):
        return "<DRNova(primary_uuid = '%s', secondary_uuid = '%s', node_name = '%s', status = '%s', other = '%s')>" % (self.primary_uuid, self.secondary_uuid, self.node_name, self.status, self.other)


