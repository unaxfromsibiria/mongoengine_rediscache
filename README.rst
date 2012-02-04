About
==========
mongoengine_rediscache allows you use cache on model level,
he can to monitor the relevance of the cache when the model changes (save, update, delete)

Dependencies
============
- pymongo
- mongoengine
- python-redis


Usage
=====
You can create models like this (for example look at models.py of application "tests")::
from mongoengine import *
from mongoengine_rediscache.fields import ReferenceFieldCached, ListFieldCached
from mongoengine_rediscache.invalidation import CacheInvalidator
from mongoengine_rediscache.queryset import CachedQuerySet
from mongoengine_rediscache import install_signals

class TestModelObj(Document, CacheInvalidator):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    text =  StringField(max_length=255, required=False )
    create_date = DateTimeField()
    
    meta = { 'queryset_class': CachedQuerySet }

class TestModelList(Document, CacheInvalidator):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    models = ListFieldCached( ReferenceField(TestModelObj) )
    
    meta = { 'queryset_class': CachedQuerySet }
    
class TestModelRef(Document, CacheInvalidator):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    model = ReferenceFieldCached(TestModelObj)
    
    meta = { 'queryset_class': CachedQuerySet }
    
install_signals('tests')

function install_signals(application name) need for update cache.

Configuration
=====
And more, you must create option in settings::
MONGOENGINE_REDISCACHE = {
    'scheme' : {
                'TestModelObj' : {
                     'request' : [ 'count', 'list', 'reference', 'get', 'list_reference' ],
                     'timeout' : 600
                     },
                'TestModelList' : {
                     'request' : [ 'count', 'list', 'reference', 'get', 'list_reference' ],
                     'timeout' : 600
                     },
                'TestModelRef' : {
                     'request' : [ 'count', 'list', 'reference', 'get', 'list_reference' ],
                     'timeout' : 600
                     },
                },
    'redis' : {
        'host': 'localhost',
        'port': 6379,
        #'db': 1, 
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
Append 'mongoengine_rediscache' in INSTALLED_APPS

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
