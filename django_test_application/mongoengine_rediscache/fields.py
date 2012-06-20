'''
Created on 12.01.2012

@author: unax
'''
from mongoengine.fields import ReferenceField, ListField
from helper import _queryset_list
from config import scheme_timelimit
from base_cache import _internal_cache as cache
from bson.dbref import DBRef
# for old version: from pymongo.dbref import DBRef

class ListFieldCached(ListField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        timeout=scheme_timelimit( instance.__class__.__name__, 'list_reference')
        changed=False
        if instance.pk is None:
            changed=True # this is new model
        else:
            try:    changed = self.name in instance._changed_fields # this model changed
            except: pass
        if (not isinstance(timeout,int)) or changed:
            return super(ListFieldCached, self).__get__(instance, owner)
        
        DBRef_list=instance._data.get(self.name)
        if isinstance(DBRef_list, _queryset_list):
            return DBRef_list
        
        if DBRef_list and len(DBRef_list)>0:
            keys=[]
            list_reference=True
            for dbref_obj in DBRef_list:
                if not isinstance(dbref_obj, DBRef):
                    list_reference = False
                    break                    
                keys.append('%s:get:pk=%s' % (dbref_obj.collection , dbref_obj.id ))
            if list_reference:
                models = cache.pipeline_get(keys)
                del keys
                if models is None or len(models) != len(DBRef_list) or changed:
                    models = super(ListFieldCached, self).__get__(instance, owner)
                    if models and len(models)>0:
                        instance._data[self.name]=_queryset_list()
                        for obj in models:
                            if not isinstance(obj, DBRef):
                                cache.set( '%s:get:pk=%s' % (obj._get_collection_name(), obj.pk), obj, timeout)
                            instance._data[self.name].append(obj)
                return models
        return super(ListFieldCached, self).__get__(instance, owner)

class ReferenceFieldCached(ReferenceField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.name)
        if isinstance(value, (DBRef)):
            timeout=scheme_timelimit(instance.__class__.__name__ , 'reference')
            if isinstance(timeout,int):
                collection = value.collection
                cache_key='%s:get:pk=%s' % (collection , value.id )
                obj=cache.get(cache_key)
                if obj is None:
                    obj = super(ReferenceFieldCached, self).__get__(instance, owner)
                    cache.set( cache_key, obj, timeout )
                if obj is not None:
                    instance._data[self.name] = obj
                return obj
        return super(ReferenceFieldCached, self).__get__(instance, owner)
