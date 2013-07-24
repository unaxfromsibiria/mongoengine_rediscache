# -*- coding: utf-8 -*-
'''
Created on 11.01.2012
@author: unax
'''
from .base_cache import _internal_cache as cache
from .config import LazySettings, ABSOLUTE_VERSION_LIMIT
from .helper import (
    _queryset_list,
    SecondaryKey)
from .invalidation import model_change
from .misc import CacheNameMixer
from mongoengine.queryset import QuerySet
from mongoengine import Document


#================ for mongoengine ====================
class CachedQuerySet(QuerySet):
    cache_scheme_dict = None

    @property
    def cache_version(self):
        version = cache.get_int("version:{0}".format(
            self._document._get_collection_name()))
        if not isinstance(version, int) or version > ABSOLUTE_VERSION_LIMIT:
            version = 1
            cache.set_int(
                "version:{0}".format(self._document._get_collection_name()),
                version,
                max([v for _, v in self.cache_scheme.iteritems()]) + 1)
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
            name.append({'skip': self._skip})
        if self._limit:
            name.append({'limit': self._limit})
        if self._ordering:
            name.append(self._ordering)
        return name.line

    def count(self):
        timeout = self.cache_scheme.get('count')
        if isinstance(timeout, int):
            core = (
                self._document._get_collection_name(),
                self.core_cache_name)
            cache_key = "{0}:count:{1}".format(*core)
            version_key = "version:{0}:{1}".format(*core)
            version = cache.get_int()
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
                cache.set_int(version_key, self.cache_version, timeout)
                cache.set_int(cache_key, n, timeout)
            del cache_key
            return n
        return super(CachedQuerySet, self).count()

    def get(self, *q_objs, **query):
        timeout = self.cache_scheme.get('get')
        document = None
        if isinstance(timeout, int):
            core_cache_name = CacheNameMixer(query)
            cache_key = "{0}:get:{1}".format(
                self._document._get_collection_name(),
                core_cache_name)
            document = cache.get(cache_key)
            if isinstance(document, SecondaryKey):
                v = document.version
                document = cache.get(document.key)
                if not isinstance(document, Document) or v < self.cache_version:
                    document = None

            if document is None:
                document = super(CachedQuerySet, self).get(*q_objs, **query)
                original_cache_key = "{0}:get:{1}".format(
                    self._document._get_collection_name(),
                    CacheNameMixer({'pk': str(document.pk)}))
                if original_cache_key != cache_key:
                    cache.set(
                        cache_key,
                        SecondaryKey(
                            original_cache_key,
                            str(document.pk),
                            self.cache_version),
                        timeout)

                cache.set(original_cache_key, document, timeout)
        else:
            document = super(CachedQuerySet, self).get(*q_objs, **query)
        return document

    @property
    def cache(self):
        timeout = self.cache_scheme.get('list')
        if isinstance(timeout, int):
            core = (
                self._document._get_collection_name(),
                self.core_cache_name)
            cache_key = "{0}:list:{1}".format(*core)
            version_key = "version:{0}:{1}".format(*core)
            version = cache.get_int(version_key)
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
                        obj_cache_key = "{0}:get:{1}".format(
                            self._document._get_collection_name(),
                            CacheNameMixer({'pk': str(obj.pk)}))
                        keys.append(obj_cache_key)
                        cache.set(obj_cache_key, obj, timeout)
                    cache.set(cache_key, keys, timeout - 1)
                    cache.set_int(version_key, self.cache_version, timeout - 1)
                del cache_key
        return self

    def update_one(self, *args, **kwargs):
        res = super(CachedQuerySet, self).update_one(*args, **kwargs)
        model_change(collection=self._document._get_collection_name())
        return res

    def update(self, *args, **kwargs):
        res = super(CachedQuerySet, self).update(*args, **kwargs)
        model_change(collection=self._document._get_collection_name())
        return res

    def delete(self, *args, **kwargs):
        res = super(CachedQuerySet, self).delete(*args, **kwargs)
        model_change(collection=self._document._get_collection_name())
        return res
