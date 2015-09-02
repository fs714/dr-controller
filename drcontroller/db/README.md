# Mariadb Information
##Mariadb in docker container on our server (15).
1. if you want to try mariadb by sql command line
    * Login to the container bash shell
          docker exec -it mariadb bash
    *  Export some ENV
         export TERM=dumb
    *  Login to mariadb
          mysql -u root -p
         (Password is 123456)

2.  Connect to database on host
    mysql -h 10.175.150.15 -P 13306 -u root -p

3.  If you want to connect to mariadb from other container:
    192.168.0.2:13306

# The DB operations module
##There are five files.
    * 'db_Dao.py' is the DB operation API ,includeing DRGlanceDao, DRNovaDao,DRNeutronDao, DRNeutronSubnetDao, DRNeutronPortDao.
    * 'models.py' defines the ORM between Objects and Models, including DRGlance, DRNova, DRNeutron, DRNeutronSubnet, DRNeutronPort.
    * 'db_test.py' is the a simple DB operations test.
    * 'init_db.py' is used to initial the DB 'dr'.
    * 'drop_db.py' is used to delete all tables of DB 'dr' 

## DB init and drop 
There is a database named 'dr' in Mariadb.

1. create tables. If you go into the 'db' dirctory ,and run 'python init_db.py', all tables in 'dr' will be created.

2. delete tables. If go into the 'db' dirctory, and run 'python init_db.py', all tables in 'dr' will be deleted.

## DB connection setting, you maybe modify db_Dao.py.

1. to connect sqlite, the process of create engine in 'db_Dao.py' should be:
   engine = create_engine("sqlite:///dr.db", echo=False)

2. to connect mariadb on host, the process of create engine in 'db_Dao.py' should be:
   engine = create_engine("mysql://root:123456@10.175.250.200:13306/dr", echo=False) 

3. to connect mariadb from other container,the process of create engine in 'db_Dao.py' should be:
   engine = create_engine("mysql://root:123456@192.168.0.2:13306/dr", echo=False) 

## How to use DB module, Take a example for DRGlanceDao

```
from db_Dao import DRGlanceDao, DRNovaDao, DRNeutronDao, DRNeutronSubnetDao, DRNeutronPortDao
from models import DRGlance, DRNova, DRNeutron, DRNeutronSubnet, DRNeutronPort

# Create a DB operation dao, such as DRGlanceDao
baseDao = DRGlanceDao() 

# Add a object, such as DRGlance
dr_glance = DRGlance(...)
baseDao.add(dr_glance)

# Get a object by primary_uuid
baseDao.get_by_primary_uuid('primary_uuid_1')

# Update a object by primary_uuid
baseDao.update_by_primary_uuid('primary_uuid_1',{'secondary_uuid':'secondary_uuid_1_update','status':'active',...})

# Delete a object by primary_uuid
baseDao.delete_by_primary_uuid('primary_uuid_1')
... ...

```
