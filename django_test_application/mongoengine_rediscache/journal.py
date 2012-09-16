# -*- coding: utf-8 -*-
'''
Created on 12.01.2012

@author: unax
'''
from base_cache import _internal_cache as cache

def add_find_record(cache_key, collection, timeout):
    try:     cache.append_to_list("%s:list:journal:" % collection, cache_key)
    except:  return

def add_count_record(cache_key, collection, timeout):
    try:     cache.append_to_list("%s:count:journal:" % collection, cache_key)
    except:  return

def add_get_record(pk, cache_key, collection, timeout):
    try:     cache.append_to_list("%s:get:journal:pk=%s" % (collection, str(pk)), cache_key)
    except:  return

def records(query_type, collection, clarify=''):
    try:     record_list = cache.get_all_list("%s:%s:journal:%s" % (collection, query_type, clarify))
    except:  record_list = []
    if query_type == 'get' and isinstance(record_list, list) and clarify != '':
        record_list.append('%s:get:%s' % (collection, clarify))
    return record_list
