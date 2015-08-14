#!/usr/bin/env python2.7

from sqlalchemy import create_engine
from sqlalchemy.orm import backref, mapper, relation, sessionmaker
from models import Base, DRGlance, DRNova, DRNeutron

# create a connection to a sqlite database and turn echo on to see the auto-generated SQL
engine = create_engine("sqlite:///dr.db", echo=False)
#engine = create_engine("mysql://test:1234@localhost/dr", echo=True)

# get a handle on the metadata
metadata = Base.metadata

# create the table
metadata.create_all(engine)

# create DBSession
DBSession = sessionmaker(bind = engine)

class BaseDao(object):
    '''
    DB based operations
    '''
    def __init__(self, table):
        self.table = table

    def getSession(self):
        return DBSession()

    def add(self, one_object):
        '''
        Add one object.

        one_object: a instance object of DRGlance, DRNova or DRNeutron
        '''
        session = self.getSession()
        session.add(one_object)
        session.commit()
        session.close()
        return 1

    def add_mult(self, object_list):
        '''
        Add multiple objects.

        object_list: a list of objects in DRGlance, DRNova or DRNeutron.
        '''
        count = len(object_list)
        session = self.getSession()
        session.add_all(object_list)
        session.commit()
        session.close()
        return count

    def get_by_primary_uuid(self, primary_uuid):
        '''
        Get one object by primary_uuid.

        class_name: DRGlance, DRNova or DRNeutron
        primary_uuid: the primary uuid of the object of DRGlance, DRNova or DRneutron
        '''
        return self.getSession().query(self.table).filter(self.table.primary_uuid==primary_uuid).first()

    def get_mult_by_primary_uuids(self, primary_uuid_list):
        '''
        Get multiple objects by primary_uuids

        class_name: DRGlance, DRNova or DRNeutron
        primary_uuid_list: a list of primary_uuids selected
        '''
        return self.getSession().query(self.table).filter(self.table.primary_uuid.in_(primary_uuid_list)).all()

    def get_all(self):
        '''
        Get all uuids including primary_uuid and secondary_uuid.

        class_name: DRGlance, DRNova or DRNeutron
        '''
        return self.getSession().query(self.table).all()

    def delete_by_primary_uuid(self, primary_uuid):
        '''
        Delete one object by primary_uuid.

        primary_uuid: the primary uuid of the object of DRGlance, DRNova or DRneutron
        '''
        session = self.getSession()
        session.delete(session.query(self.table).filter(self.table.primary_uuid==primary_uuid).first())
        session.commit()
        session.close()
        return 1

    def delete_mult_by_primary_uuids(self, primary_uuid_list):
        '''
        Delete multiple objects.

        class_name: DRGlance, DRNova or DRNeutron
        primary_uuid_list: a list of primary_uuids selected
        '''
        count = 0
        session = self.getSession()
        for primary_uuid in primary_uuid_list:
            session.delete(session.query(self.table).filter(self.table.primary_uuid==primary_uuid).first())
            count = count+1
        session.commit()
        session.close()
        return count



class DRGlanceDao(BaseDao):

    def __init__(self, DRGlance):
        super(DRGlanceDao, self).__init__(DRGlance)

    '''
    other specific method
    '''

class DRNovaDao(BaseDao):

    def __init__(self, DRNova):
        super(DRGlanceDao, self).__init__(DRNova)

class DRNeutronDao(BaseDao):

    def __init__(self, DRNova):
        super(DRNeutronDao, self).__init_-(DRNeutron)






