# -*- coding: utf-8 -*-
'''
Created on 11.01.2012
@author: unax
'''
from mongoengine.queryset import QuerySet
from misc import CacheNameMixer
from __init__ import _queryset_list, scheme_timelimit
from __init__ import _internal_cache as cache
import journal

#================ for mongoengine ====================

class CachedQuerySet(QuerySet):
    @property
    def core_cache_name(self):
        name=CacheNameMixer(self._query)
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
        timeout=scheme_timelimit(self._document.__name__, 'count')
        if isinstance(timeout,int):
            cache_key="%s:count:%s" % (self._document._get_collection_name(), self.core_cache_name )
            n=cache.get(cache_key)
            if n is None:
                if self._limit == 0:
                    return 0
                n=self._cursor.count(with_limit_and_skip=True)
                cache.set( cache_key, n, timeout )
                # add in journal
                journal.add_count_record(cache_key, self._document._get_collection_name() , timeout)
            del cache_key
            return n
        return super(CachedQuerySet, self).count()
    
    def get(self, *q_objs, **query):
        timeout=scheme_timelimit(self._document.__name__, 'get')
        document=None
        if isinstance(timeout,int):
            core_cache_name=str(CacheNameMixer(query))
            cache_key="%s:get:%s" % ( self._document._get_collection_name() , core_cache_name)
            document=cache.get(cache_key)
            if document is None:
                self.__call__(*q_objs, **query)
                count = super(CachedQuerySet, self).count()
                if count == 1:
                    document = self[0]
                elif count > 1:
                    raise self._document.MultipleObjectsReturned(u'%d items returned, instead of 1' % count)
                elif count < 1:
                    raise self._document.DoesNotExist(u"%s matching query does not exist."% self._document._class_name)
                cache.set( cache_key, document, timeout )
                journal.add_get_record(document.pk, cache_key, self._document._get_collection_name(), timeout)
        else:
            document=super(CachedQuerySet, self).get(*q_objs, **query)
        return document

    @property
    def cache(self):
        timeout=scheme_timelimit(self._document.__name__, 'list')
        if isinstance(timeout,int):
            cache_key="%s:list:%s" % (self._document._get_collection_name(), self.core_cache_name )
            cached_list=cache.get(cache_key)
            if cached_list is None:
            # creating cache
                cached_list=_queryset_list()
                if super(CachedQuerySet, self).count()>0:
                    for obj in self:
                        cached_list.append(obj)
                    cache.set( cache_key, cached_list, timeout )
                    # add in journal
                    journal.add_find_record(cache_key, self._document._get_collection_name() , timeout)
            del cache_key
            return cached_list
        return self
