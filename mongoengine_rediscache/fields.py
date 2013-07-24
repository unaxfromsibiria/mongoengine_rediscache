'''
Created on 12.01.2012

@author: unax
'''
from .config import LazySettings
from .helper import _queryset_list
from .misc import CacheNameMixer
from mongoengine import (
    ReferenceField,
    ListField,
    Document)
from mongoengine.queryset import QuerySet
from base_cache import _internal_cache as cache
from bson.dbref import DBRef


def _get_timeout(instance, operaton):
    scheme = LazySettings().scheme.get('{0}.{1}'\
        .format(instance.__module__, instance.__class__.__name__))
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
                # this is new model
                changed = True
            else:
                changed = instance._changed_fields\
                    and self.name in instance._changed_fields

            if (not isinstance(timeout, int)) or changed:
                return super(ListFieldCached, self).__get__(instance, owner)

            DBRef_list = instance._data.get(self.name)

            if isinstance(DBRef_list, (list, tuple, QuerySet)):
                for d in DBRef_list:
                    if isinstance(d, Document):
                        return DBRef_list

            if DBRef_list and len(DBRef_list) > 0:
                keys = []
                for dbref_obj in DBRef_list:
                    if isinstance(dbref_obj, DBRef):
                        keys.append('{0}:get:{1}'.format(
                            dbref_obj.collection,
                            CacheNameMixer({'pk': str(dbref_obj.id)})))
                    elif isinstance(dbref_obj, (str, unicode)):
                        keys.append('{0}:get:{1}'.format(
                            self.document_type._get_collection_name(),
                            CacheNameMixer({'pk': str(dbref_obj)})))

                models = cache.pipeline_get(keys)
                del keys
                # if models is None or len(models) != len(DBRef_list) or changed: - this right, but
                if models is None or len(models) < 1 or changed:
                    # it reduces operations count
                    models = super(ListFieldCached, self).__get__(instance, owner)

                    if models and len(models) > 0:
                        instance._data[self.name] = _queryset_list()
                        for obj in models:
                            if isinstance(obj, Document):
                                cache.set('{0}:get:{1}'.format(
                                    obj._get_collection_name(),
                                    CacheNameMixer({'pk': str(obj.pk)})),
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
            # for mongoengine dbref=False options
            if not isinstance(value, Document):
                if isinstance(timeout, int):
                    core = None
                    if isinstance(value, DBRef):
                        core = (value.collection,
                                CacheNameMixer({'pk': str(value.id)}))
                    elif isinstance(value, (str, unicode)):
                        core = (self.document_type._get_collection_name(),
                                CacheNameMixer({'pk': str(value)}))
                    if core:
                        cache_key = '{0}:get:{1}'.format(*core)
                        obj = cache.get(cache_key)
                        if obj is None:
                            obj = super(ReferenceFieldCached, self)\
                                .__get__(instance, owner)
                            if obj:
                                cache.set(cache_key, obj, timeout)
                        instance._data[self.name] = obj

        return super(ReferenceFieldCached, self).__get__(instance, owner)
