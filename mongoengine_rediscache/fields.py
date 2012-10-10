'''
Created on 12.01.2012

@author: unax
'''
from mongoengine import (
    ReferenceField,
    ListField,
    Document)
from helper import _queryset_list
from base_cache import _internal_cache as cache
from bson.dbref import DBRef
from config import LazySettings
from misc import CacheNameMixer

def _get_timeout(instance, operaton):
    scheme = LazySettings().scheme.get('%s.%s' % (instance.__module__, instance.__class__.__name__))
    if scheme and operaton in scheme:
        return int(scheme.get(operaton))
    return None

class ListFieldCached(ListField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        timeout = _get_timeout(instance, 'list_reference')
        if timeout:
            changed = False
            if instance.pk is None:
                changed = True # this is new model
            else:
                try:    changed = self.name in instance._changed_fields # this model changed
                except: pass
    
            if (not isinstance(timeout, int)) or changed:
                return super(ListFieldCached, self).__get__(instance, owner)
            
            DBRef_list = instance._data.get(self.name)
            if isinstance(DBRef_list, _queryset_list):
                return DBRef_list
            if DBRef_list and len(DBRef_list) > 0:
                keys = []
    
                for dbref_obj in DBRef_list:
                    if isinstance(dbref_obj, DBRef):
                        keys.append('%s:get:%s' % (dbref_obj.collection,
                                                   CacheNameMixer({ 'pk' : str(dbref_obj.id) }) ) )
                    else:
                        keys.append('%s:get:%s' % (self.document_type._get_collection_name(),
                                                   CacheNameMixer({ 'pk' : str(dbref_obj)}) ) )
    
                models = cache.pipeline_get(keys)
                del keys
                if models is None or len(models) != len(DBRef_list) or changed:
                    models = super(ListFieldCached, self).__get__(instance, owner)
    
                    if models and len(models) > 0:
                        instance._data[self.name] = _queryset_list()
                        for obj in models:
                            if isinstance(obj, Document):
                                cache.set('%s:get:%s' % (obj._get_collection_name(),
                                                         CacheNameMixer({ 'pk' : str(obj.pk) }) ),
                                          obj, timeout)
                                instance._data[self.name].append(obj)
                return models
        return super(ListFieldCached, self).__get__(instance, owner)

class ReferenceFieldCached(ReferenceField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        timeout = _get_timeout(instance, 'reference')
        if timeout:    
            value = instance._data.get(self.name)
            if not isinstance(value, Document): # for mongoengine dbref=False options
                if isinstance(timeout, int):
                    core = None
                    if isinstance(value, DBRef):
                        core = (value.collection,
                                CacheNameMixer({ 'pk' : str(value.id) }) )
                    else:
                        core = (self.document_type._get_collection_name(),
                                CacheNameMixer({ 'pk' : str(value) }) )

                    cache_key = '%s:get:%s' % core
                    obj = cache.get(cache_key)

                    if obj is None:
                        obj = super(ReferenceFieldCached, self).__get__(instance, owner)
                        if obj:
                            cache.set(cache_key, obj, timeout)
                    instance._data[self.name] = obj

        return super(ReferenceFieldCached, self).__get__(instance, owner)
