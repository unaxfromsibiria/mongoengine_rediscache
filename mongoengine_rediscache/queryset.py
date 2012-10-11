# -*- coding: utf-8 -*-
'''
Created on 11.01.2012
@author: unax
'''
from mongoengine.queryset import QuerySet
from mongoengine import Document
from helper import (
    _queryset_list,
    SecondaryKey)
from config import LazySettings, ABSOLUTE_VERSION_LIMIT
from misc import CacheNameMixer
from base_cache import _internal_cache as cache
from invalidation import model_change

#================ for mongoengine ====================

class CachedQuerySet(QuerySet):
    cache_scheme_dict = None

    @property
    def cache_version(self):
        version = cache.get_int("version:%s" % self._document._get_collection_name())
        if not isinstance(version, int) or version > ABSOLUTE_VERSION_LIMIT:
            version = 1
            cache.set_int("version:%s" % self._document._get_collection_name(),
                          version,
                          max([ v for k, v in self.cache_scheme.iteritems() ]) + 1)
        return version

    @property
    def cache_scheme(self):
        if self.cache_scheme_dict is None:
            self.cache_scheme_dict = dict()
            d = LazySettings().scheme.get('%s.%s' % (self._document.__module__,
                                                     self._document.__name__))
            if d:
                self.cache_scheme_dict.update(**d)
        return self.cache_scheme_dict

    @property
    def core_cache_name(self):
        name = CacheNameMixer(self._query)
        if not name.exist:
            name.append(('all',))
        if self._skip:
            name.append({ 'skip'  : self._skip })
        if self._limit:
            name.append({ 'limit' : self._limit })
        if self._ordering:
            name.append(self._ordering)
        return name.line

    def count(self):
        timeout = self.cache_scheme.get('count')
        if isinstance(timeout, int):
            core = (self._document._get_collection_name(), self.core_cache_name)
            cache_key = "%s:count:%s" % core
            version = cache.get_int("version:%s:%s" % core)
            if version:
                v = self.cache_version
                n = cache.get_int(cache_key)
            else:
                v = None
                n = None

            if not isinstance(n, int) or version != v:
                if self._limit == 0:
                    n = 0
                else:
                    n = self._cursor.count(with_limit_and_skip=True)
                cache.set_int("version:%s:%s" % core, self.cache_version, timeout)
                cache.set_int(cache_key, n, timeout)
            del cache_key
            return n
        return super(CachedQuerySet, self).count()

    def get(self, *q_objs, **query):
        timeout = self.cache_scheme.get('get')
        document = None
        if isinstance(timeout, int):
            core_cache_name = CacheNameMixer(query)
            cache_key = "%s:get:%s" % (self._document._get_collection_name(),
                                       core_cache_name)
            document = cache.get(cache_key)
            if isinstance(document, SecondaryKey):
                original_pk = document.pk
                v = document.version
                document = cache.get(document.key)
                if not isinstance(document, Document) or v<self.cache_version:
                    document = self.get(pk=original_pk)

            elif document is None:
                self.__call__(*q_objs, **query)
                count = super(CachedQuerySet, self).count()
                if count == 1:
                    document = self[0]
                elif count > 1:
                    raise self._document.MultipleObjectsReturned(u'%d items returned, instead of 1' % count)
                elif count < 1:
                    raise self._document.DoesNotExist(u"%s matching query does not exist." % self._document._class_name)
                
                original_cache_key = "%s:get:%s" % (self._document._get_collection_name(),
                                                    CacheNameMixer({ 'pk' : str(document.pk) }))
                if original_cache_key != cache_key:
                    cache.set(cache_key,
                              SecondaryKey(original_cache_key, str(document.pk), self.cache_version),
                              timeout)

                cache.set(original_cache_key, document, timeout)
        else:
            document = super(CachedQuerySet, self).get(*q_objs, **query)
        return document

    @property
    def cache(self):
        timeout = self.cache_scheme.get('list')
        if isinstance(timeout, int):
            core = (self._document._get_collection_name(), self.core_cache_name)
            cache_key = "%s:list:%s" % core
            version = cache.get_int("version:%s:%s" % core)
            if isinstance(version, int):
                v = self.cache_version
                cached_list = cache.get(cache_key)
            else:
                v = None
                cached_list = None

            if isinstance(cached_list, list) and version == v:
                del cache_key
                return _queryset_list(cache.pipeline_get(cached_list))
            else:
                # creating cache
                if self.count() > 0:
                    keys = list()
                    for obj in self:
                        obj_cache_key = "%s:get:%s" % (self._document._get_collection_name(),
                                                       CacheNameMixer({ 'pk' : str(obj.pk) }))
                        keys.append(obj_cache_key)
                        cache.set(obj_cache_key, obj, timeout)
                    cache.set(cache_key, keys, timeout - 1)
                    cache.set_int("version:%s:%s" % core, self.cache_version, timeout - 1)
                del cache_key
        return self

    def update_one(self, safe_update=True, upsert=False, write_options=None, **update):
        res = QuerySet.update_one(self, safe_update=safe_update, upsert=upsert, write_options=write_options, **update)
        model_change(collection=self._document._get_collection_name())
        return res

    def update(self, safe_update=True, upsert=False, multi=True, write_options=None, **update):
        res = QuerySet.update(self, safe_update=safe_update, upsert=upsert, multi=multi, write_options=write_options, **update)
        model_change(collection=self._document._get_collection_name())
        return res

    def delete(self, safe=False):
        res = QuerySet.delete(self, safe=safe)
        model_change(collection=self._document._get_collection_name())
        return res
