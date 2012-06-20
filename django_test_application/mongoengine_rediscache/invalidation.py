'''
Created on 13.01.2012

@author: unax
'''

from journal import records
from base_cache import _internal_cache as cache

def model_change(pk, collection):
    cache.pipeline_delete(records('list', collection))
    cache.pipeline_delete(records('count', collection))
    cache.pipeline_delete(records('get',collection,'pk=%s' % str(pk) ))
    cache.delete("%s:get:journal:pk=%s" % (collection, str(pk)))
    cache.delete("%s:list:journal:" % collection )
    cache.delete("%s:count:journal:" % collection )

class CacheInvalidator:
    @classmethod
    def post_save(cls, sender, document, **kwargs):
        model_change(document.pk, document._get_collection_name())
                
    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        model_change(document.pk, document._get_collection_name())
