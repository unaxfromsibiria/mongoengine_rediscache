# -*- coding: utf-8 -*-
'''
Created on 11.01.2012
@author: unax
'''
from django.conf import settings
from mongoengine.queryset import QuerySet, QCombination
from misc import CacheNameMixer
from __init__ import _queryset_list
from __init__ import _internal_cache as cache
import journal
#================ for mongoengine ====================

DEFAULT_TIMEOUT=60

class CachedQuerySet(QuerySet):
    
    def get(self, *q_objs, **query):
        scheme=settings.MONGOENGINE_REDISCACHE.get('scheme').get( self._document.__name__ )
        document=None
        if scheme and 'get' in scheme.get('request'):
            core_cache_name=str(CacheNameMixer(query))
            cache_key="%s:get:%s" % ( self._document._get_collection_name() , core_cache_name)
            document=cache.get(cache_key)
            if document is None:
                document=super(CachedQuerySet, self).get(*q_objs, **query)
                try:
                    timeout= int(scheme.get('timeout'))
                except:
                    timeout= DEFAULT_TIMEOUT
                cache.set( cache_key, document, timeout )
                journal.add_get_record(document.pk, cache_key, self._document._get_collection_name(), timeout)
        else:
            document=super(CachedQuerySet, self).get(*q_objs, **query)
        return document

    @property
    def core_cache_name(self):
        if isinstance(self._query_obj, QCombination):
            name=CacheNameMixer(self._mongo_query)
        else:
            name=CacheNameMixer(self._query_obj.query)
        if not name.exist:
            name.append(('all',))
        if self._skip:
            name.append({ 'skip'  : self._skip })
        if self._limit:
            name.append({ 'limit' : self._limit })
        if self._ordering:
            name.append(self._ordering)
        return name.line

    @property
    def cache(self):
        scheme=settings.MONGOENGINE_REDISCACHE.get('scheme').get( self._document.__name__ )
        if 'list' in scheme.get('request'):
            cache_key="%s:list:%s" % (self._document._get_collection_name(), self.core_cache_name )
            cached_list=cache.get(cache_key)
            if cached_list is None:
            # creating cache
                cached_list=_queryset_list()
                if super(CachedQuerySet, self).count()>0:
                    for obj in self:
                        cached_list.append(obj)
                    try:
                        timeout= int(scheme.get('timeout'))
                    except:
                        timeout= DEFAULT_TIMEOUT
                    cache.set( cache_key, cached_list, timeout )
                    # add in journal
                    journal.add_find_record(cache_key, self._document._get_collection_name() , timeout)
            del cache_key
            return cached_list
        return self
    
    def count(self):
        scheme=settings.MONGOENGINE_REDISCACHE.get('scheme').get( self._document.__name__ )
        if 'count' in scheme.get('request'):
            cache_key="%s:count:%s" % (self._document._get_collection_name(), self.core_cache_name )
            n=cache.get(cache_key)
            if n is None:
                n=super(CachedQuerySet, self).count()
                try:
                    timeout= int(scheme.get('timeout'))
                except:
                    timeout= DEFAULT_TIMEOUT
                cache.set( cache_key, n, timeout )
                # add in journal
                journal.add_count_record(cache_key, self._document._get_collection_name() , timeout)
            del cache_key
            return n
        return super(CachedQuerySet, self).count()
