# The DB operations module
There are three files.
'db.py' is the DB operation API.
'models.py' defines the ORM between Objects and Models, including DRGlance, DRNova, DRNeutron.
'db_test.py' is the a simple DB operations test.

## How to use DB module
```
from db import *
from models import *

# Create a DB operation dao, such as DRGlanceDao
baseDao = DRGlanceDao(DRGlance) 

# Add a object, such as DRGlance
dr_glance = DRGlance(...)
baseDao.add(dr_glance)

# Get a object by primary_uuid
baseDao.get_by_primary_uuid(...)

....

```
