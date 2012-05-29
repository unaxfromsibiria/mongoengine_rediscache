# -*- coding: utf-8 -*-
'''
Created on 12.01.2012

@author: unax
'''
from __init__ import _internal_cache as cache

def add_find_record(cache_key, collection, timeout ):
    try:
        journal_name="%s:list:journal:" % collection
    except:
        return
    journal_list=cache.get(journal_name)
    if journal_list is None:
        journal_list=[]
    journal_list.append(cache_key)
    cache.set(journal_name,journal_list,timeout)

def add_count_record(cache_key, collection, timeout ):
    try:
        journal_name="%s:count:journal:" % collection
    except:
        return
    journal_list=cache.get(journal_name)
    if journal_list is None:
        journal_list=[]
    journal_list.append(cache_key)
    cache.set(journal_name,journal_list,timeout)

def add_get_record(pk, cache_key, collection, timeout):
    try:
        journal_name="%s:get:journal:pk=%s" % (collection, str(pk))
    except:
        return
    journal_list=cache.get(journal_name)
    if journal_list is None:
        journal_list=[]
    journal_list.append(cache_key)
    cache.set(journal_name,journal_list,timeout)

def records(query_type, collection, clarify=''):
    try:
        record_list=cache.get("%s:%s:journal:%s" % (collection, query_type, clarify))
    except:
        record_list=None
    if query_type == 'get' and isinstance(record_list,list) and clarify!='':
        record_list.append('%s:get:%s' % (collection,clarify) )
    return record_list
