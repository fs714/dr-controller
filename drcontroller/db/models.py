#!/usr/bin/env python2.7
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker

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
    other = Column(String(50))
    
    def __repr__(self):
        return "<DRGlance(primary_uuid = '%s', secondary_uuid = '%s', other = '%s')>" % (self.primary_uuid, self.secondary_uuid, self.other)   


class DRNeutron(Base):
    '''
    Model class DRNeutron
    '''
    __tablename__ = "dr_neutron"

    id = Column(Integer, Sequence('dr_glance_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    forward = Column(String(255))
    request = Column(String(255))
    other =  Column(String(50))

class DRNova(Base):
    '''
    Model Class DRNova
    '''
    __tablename__ = "dr_nova"

    id = Column(Integer, Sequence('dr_glance_id_seq'), primary_key = True)
    primary_uuid = Column(String(50))
    secondary_uuid = Column(String(50))
    node_name = Column(String(50))
    other = Column(String(50))
