'''
Created on 13.01.2012

@author: unax
'''

from journal import records
from __init__ import _internal_cache as cache

def model_change(pk, collection):
    cache.pipeline_delete(records('list', collection))
    cache.pipeline_delete(records('get',collection,'pk=%s' % str(pk) ))
    cache.delete("%s:get:journal:pk=%s" % (collection, str(pk)))
    cache.delete("%s:list:journal:" % collection )

class CacheInvalidator:
    @classmethod
    def post_save(cls, sender, document, **kwargs):
        model_change(document.pk, document._get_collection_name())
                
    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        model_change(document.pk, document._get_collection_name())

