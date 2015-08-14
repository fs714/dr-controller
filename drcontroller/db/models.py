#!/usr/bin/env python2.7

from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
        return "<DRGlance(primary_uuid = '%s', secondary_uuid = '%s', other = '%s')>" % (self.primary_uuid, self.secondary_uuid, self.other)


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
    other =  Column(String(50))

    def __repr__(self):
        return "<DRNeutron(primary_uuid = '%s', secondary_uuid = '%s', forward = '%s', request='%s',other = '%s')>" %\
                (self.primary_uuid, self.secondary_uuid, self.forward, self.request, self.other)

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
    other = Column(String(50))

    def __repr__(self):
        return "<DRNova(primary_uuid = '%s', secondary_uuid = '%s', node_name = '%s', other = '%s')>" % (self.primary_uuid, self.secondary_uuid, self.node_name, self.other)


