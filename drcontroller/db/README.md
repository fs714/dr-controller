# The DB operations module
There are three files.
'db_Dao.py' is the DB operation API.
'models.py' defines the ORM between Objects and Models, including DRGlance, DRNova, DRNeutron.
'db_test.py' is the a simple DB operations test.

## How to use DB module
## Take a example for DRGlanceDao
```
from db_Dao import DRGlanceDao, DRNovaDao, DRNeutronDao
from models import DRGlance, DRNova, DRNeutron

# Create a DB operation dao, such as DRGlanceDao
baseDao = DRGlanceDao(DRGlance) 

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
