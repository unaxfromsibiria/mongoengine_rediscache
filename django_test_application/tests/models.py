'''
Created on 24.01.2012

@author: unax
'''

from datetime import datetime
from mongoengine import *
from mongoengine_rediscache.fields import ReferenceFieldCached, ListFieldCached
from mongoengine_rediscache.invalidation import CacheInvalidator
from mongoengine_rediscache.queryset import CachedQuerySet
from mongoengine_rediscache import install_signals

class TestModelObj(Document, CacheInvalidator):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    text =  StringField(max_length=255, required=False )
    create_date = DateTimeField(default=datetime.now())
    
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

