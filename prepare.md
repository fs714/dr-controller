#this file use to prepare some libs for python 
```BASH
apt-get update

apt-get install python
apt-get install python-pip
apt-get install python-mysqldb (required by using SQLAlchemy)
apt-get install python-dev (required by pycrpto)

pip install –r requirements.txt (ansible, taskflow, SQLAlchemy have been in it)

pip install python-neutronclient
pip install python-novaclient
pip install python-keystoneclient
apt-get install python-glanceclient
```
