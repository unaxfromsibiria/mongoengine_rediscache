'''
Created on 13.09.2012

@author: unax
'''

from mongoengine import *
from mongoengine import CASCADE as REF_CASCADE
from mongoengine import PULL as REF_PULL
from datetime import datetime
from mongoengine_rediscache.config import LazySettings
from mongoengine_rediscache import install_signals
from mongoengine_rediscache.queryset import CachedQuerySet
from mongoengine_rediscache.fields import ReferenceFieldCached, ListFieldCached

LazySettings.options = {
    'scheme' : {
                'models.Model1' : { 'all' : 600 },
                'models.Model2' : { 'all' : 600 },
                'models.Model3' : { 'all' : 600 },
                },
    'redis' : {
        'host': 'localhost',
        'port': 6379,
        'db'  : 2,
        'socket_timeout': 5,
    },
    'used'      : True,
    'keyhashed' : 'crc',
}

class Model1(Document):
    name = StringField(max_length=32)
    volume = IntField()
    created = DateTimeField(default=datetime.now)
    
    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }

class Model2(Document):
    name = StringField(max_length=32)
    count = IntField()
    created = DateTimeField(default=datetime.now)
    model1 = ReferenceFieldCached(Model1, reverse_delete_rule=REF_CASCADE, dbref=False)
    
    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }

class Model3(Document):
    name = StringField(max_length=32)
    count = IntField()
    created = DateTimeField(default=datetime.now)
    model1 = ListFieldCached(ReferenceField(Model1, reverse_delete_rule=REF_CASCADE, dbref=False), required=True)
    
    meta = { 'queryset_class': CachedQuerySet, 'cascade' : False }

install_signals()