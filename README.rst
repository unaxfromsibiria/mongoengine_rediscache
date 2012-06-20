About
==========
:Info: Redis cached tools for caching MongoEngine ORM models
:Author: Michael

mongoengine_rediscache allows you use cache on model level,
he can to monitor the relevance of the cache when the model changes (save, update, delete)

Dependencies
============
- pymongo
- mongoengine
- python-redis
- `blinker <http://pypi.python.org/pypi/blinker#downloads>`_

Usage
=====
You can create models like this (for example look at models.py of application "tests")::

	from mongoengine import *
	from mongoengine_rediscache.fields import ReferenceFieldCached, ListFieldCached
	from mongoengine_rediscache.queryset import CachedQuerySet
	
	class TestModelObj(Document):
	    num  =  IntField(default=0)
	    name =  StringField(max_length=255, required=False )
	    text =  StringField(max_length=255, required=False )
	    create_date = DateTimeField()
	    
	    meta = { 'queryset_class': CachedQuerySet }
	
	class TestModelList(Document):
	    num  =  IntField(default=0)
	    name =  StringField(max_length=255, required=False )
	    models = ListFieldCached( ReferenceField(TestModelObj) )
	    
	    meta = { 'queryset_class': CachedQuerySet }
	    
	class TestModelRef(Document):
	    num  =  IntField(default=0)
	    name =  StringField(max_length=255, required=False )
	    model = ReferenceFieldCached(TestModelObj)
	    
	    meta = { 'queryset_class': CachedQuerySet }
	   
	   
Possible you can achieve greater efficiency if turn off cascade save for models with ReferenceField::

	class TestModelRef(Document):
	    num  =  IntField(default=0)
	    name =  StringField(max_length=255, required=False )
	    model = ReferenceFieldCached(TestModelObj)
	    
	    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }
	    
	    
Make sure the 'mongoengine_rediscache' after a 'you_application' in INSTALLED_APPS (all your applications)::

	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.sitemaps',
	    'django.contrib.staticfiles',
	    'django.contrib.admin',
	    'packeris',
	    'tests',
	    'mongoengine_rediscache',
	    'cronis',
	)


Configuration
=====
And more, you must create option in settings::

	MONGOENGINE_REDISCACHE = {
	    'scheme' : {
                	'tests.models.TestModelObj'  : { 'list' : 120, 'reference' : 600, 'get' : 600 },
                	'tests.models.TestModelList' : { 'all' : 600 },
                	'tests.models.TestModelRef'  : { 'list' : 120, 'reference' : 600, 'get' : 120, 'list_reference' : 600 },
                	'tests.models.TestModelDict' : { 'list' : 120, 'reference' : 600, 'get' : 120, 'list_reference' : 600 },
	                },
	    'redis' : {
	        'host': 'localhost',
	        'port': 6379,
	        'db': 1, 
	        'socket_timeout': 3,
	    },
	    'used' : True,
	    'keyhashed' : True,
	}

- `'count' - use cache for count() method of CachedQuerySet`
- `'list' - use cache in CachedQuerySet, you just need to call property ".cache" after of all "filter" and "order_by"`
- `'reference' - use cache in ReferenceFieldCached`
- `'get' - use cache in CachedQuerySet for all get request`
- `'list_reference' - use cache for ListFieldCached( ReferenceField(Document) )`
I think this all clear..

MONGOENGINE_REDISCACHE contain option 'keyhashed' needed for hashed cahce keys.

If 'keyhashed' is False then cache name generator will be create keys like this::
  1) "test_model_obj:list:_types=TestModelObj|text=regex(ef)|num=$lt=500000|create_date=$gt=1986-11-2207:15:00|((num,1))"
  2) "test_model_obj:list:text__contains=aa|((num,1))"
  3) "test_model_obj:list:_types=TestModelObj|text=regex(fe)|num=$lt=500000|((num,1))"
  4) "test_model_obj:list:name__contains=ee|((name,-1))"
  5) "test_model_obj:list:_types=TestModelObj|create_date=$gt=1986-11-2207:15:00|name=regex(bb)|((name,-1))"

If 'keyhashed' is True then keys will be hide in hash::
  1) "test_model_obj:list:9cc7bcf436afe1db24bb4aaae89f429f"
  2) "test_model_obj:list:c96fc2fe93b665c8f44dbf1ae4b1dacf"
  3) "test_model_obj:list:7828697e5b6c1995e3f5d4e336acb30d"
  4) "test_model_obj:list:b212d48e0a087b249b9701dee2e056c2"
  5) "test_model_obj:list:8eae9ba432e723cdc43f3399e50ec41f"

This will be useful if you have a lot of different samples of one collection.

and finally
=====
Hopefully this will be useful :)

Thanks for the idea of Alexander Schepanovski (author of https://github.com/Suor/django-cacheops)

Sincerely, Michael Vorotyntsev.
