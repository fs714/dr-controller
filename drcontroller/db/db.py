#!/usr/bin/env python2.7

from sqlalchemy import create_engine
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from models import Base, DRGlance, DRNova, DRNeutron
import functools

# create a connection to a sqlite database and turn echo on to see the auto-generated SQL
engine = create_engine("sqlite:///dr.db", echo=False)
#engine = create_engine("mysql://test:1234@localhost/dr", echo=True)

# get a handle on the metadata
metadata = Base.metadata

# create the table 
metadata.create_all(engine)

# create a db session instance
DBSession = sessionmaker(bind=engine)

def add(one_object):
    '''
    Add one object.
   
    one_object: a instance object of DRGlance, DRNova or DRNeutron
    '''
    count = 1
    session = DBSession()
    session.add(one_object)
    session.commit()
    session.close()
    return count

def add_mult(object_list):
    '''
    Add multiple objects.
    
    object_list: a list of objects in DRGlance, DRNova or DRNeutron.
    '''
    count = len(object_list)
    session = DBSession()
    session.add_all(object_list)
    session.commit()
    session.close()
    return count  

def get_by_primary_uuid(class_name, primary_uuid):
    '''
    Get one object by primary_uuid.

    class_name: DRGlance, DRNova or DRNeutron
    primary_uuid: the primary uuid of the object of DRGlance, DRNova or DRneutron 
    '''
    session = DBSession()
    one_object= session.query(class_name).filter(class_name.primary_uuid==primary_uuid).first()
    session.close()
    return one_object

def get_mult_by_primary_uuids(class_name, primary_uuid_list):
    '''
    Get multiple objects by primary_uuids
    
    class_name: DRGlance, DRNova or DRNeutron
    primary_uuid_list: a list of primary_uuids selected 
    '''
    return DBSession().query(class_name).filter(class_name.primary_uuid.in_(primary_uuid_list)).all()

def get_all(class_name):
    '''
    Get all uuids including primary_uuid and secondary_uuid.
    
    class_name: DRGlance, DRNova or DRNeutron 
    '''
    session = DBSession()
    uuids = session.query(class_name).all()
    session.close()
    return uuids

def delete_by_primary_uuid(class_name, primary_uuid):
    '''
    Delete one object by primary_uuid.
    
    class_name: DRGlance, DRNova or DRNeutron
    primary_uuid: the primary uuid of the object of DRGlance, DRNova or DRneutron
    '''
    count = 1
    session = DBSession()
    one_object = session.query(class_name).filter(class_name.primary_uuid==primary_uuid).first()
    session.delete(one_object)
    session.commit()
    session.close()
    return count

def delete_mult_by_primary_uuids(class_name, primary_uuid_list):
    '''
    Delete multiple objects.
    
    class_name: DRGlance, DRNova or DRNeutron
    primary_uuid_list: a list of primary_uuids selected 
    '''
    count = 0
    session = DBSession()
    for primary_uuid in primary_uuid_list:
      session.delete(session.query(class_name).filter(class_name.primary_uuid==primary_uuid).first())
      count = count+1
    session.commit()
    session.close()
    return count 

def update():   
    pass

def test():
    '''
    This is a test for ADD, GET, DELETE, UPDATE
    '''    
    print '<`%s` add one>:%s' % (DRGlance.__name__, add(DRGlance(primary_uuid = "glance_primary_uuid_1",\
                                                                secondary_uuid = "glance_secondary_uuid_1",\
                                                                other="other_information")))
    print '<`%s` add multiple>:%s' % (DRGlance.__name__, add_mult([DRGlance(primary_uuid = "glance_primary_uuid_2",\
                                                                            secondary_uuid = "glance_secondary_uuid_2",\
                                                                            other="other_information"),\
                                                                   DRGlance(primary_uuid = "glance_primary_uuid_3",\
                                                                            secondary_uuid = "glance_secondary_uuid_3",\
                                                                            other="other_information")]))
    '''
    add(DRNova(primary_uuid="nova_primary_uuid_1", secondary_uuid="nova_primary_uuid_1", node_name="nova_node_name_1", other="other_information"))  
    add_mult([DRNova(primary_uuid = "nova_primary_uuid_2",\
                     secondary_uuid = "nova_secondary_uuid_2",\
                     node_name="nova_node_name_2", other="other_information"),\
              DRNova(primary_uuid = "nova_primary_uuid_3",\
                     secondary_uuid = "nova_secondary_uuid_3",\
                     node_name="nova_node_name2",\
                     other="other_information")])
    
    add(DRNeutron(primary_uuid="neutron_primary_uuid_1", secondary_uuid="neutron_primary_uuid_1", forward="forward_1", request="request_1", other="other_information"))
    add_mult([DRNeutron(primary_uuid="neutron_primary_uuid_2",\
                        secondary_uuid="neutron_secondary_uuid_2",\
                        forward="forward_2",\
                        request="request_2",\
                        other="other_information"),\
              DRNeutron(primary_uuid="neutron_primary_uuid_3",\
                        secondary_uuid="neutron_secondary_uuid_3",\
                        forward="forward_3",\
                        request="request_3",\
                        other="other_information")])
    '''

    print '<`%s` get one object >: %s' % (DRGlance.__name__, get_by_primary_uuid(DRGlance,primary_uuid='glance_primary_uuid_1'))
    print '<`%s` get multiple objects>: %s' % (DRGlance.__name__, get_mult_by_primary_uuids(DRGlance, ['glance_primary_uuid_1', 'glance_primary_uuid_4']))
    print '<`%s` get all >: %s' % (DRGlance.__name__, get_all(DRGlance))      
       
    print '<`%s` delete one >: %s' % (DRGlance.__name__, delete_by_primary_uuid(DRGlance,'glance_primary_uuid_1'))
    print '<`%s` delete multiple >: %s' % (DRGlance.__name__, delete_mult_by_primary_uuids(DRGlance,['glance_primary_uuid_2','glance_primary_uuid_3']))

if __name__ == '__main__':
    test()
    print DRGlance 
