'''
Created on 13.01.2012

@author: unax
'''
SERVICE_TIME = 60
from base_cache import _internal_cache as cache
from misc import CacheNameMixer

def model_change(**params):
    pk = params.get('pk')
    collection = params.get('collection')
    document = params.get('document')
    if document:
        pk = document.pk
        collection = document._get_collection_name()
    key = "%s:get:%s" % (collection, CacheNameMixer({ 'pk' : str(pk) }))
    if document:
        cache.set(key, document, SERVICE_TIME)
    if params.get('delete'):
        cache.delete(key)
    cache.incr("version:%s" % collection, 1)

class CacheInvalidator:
    @classmethod
    def post_save(cls, sender, document, **kwargs):
        model_change(document=document)

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        model_change(pk=document.pk, collection=document._get_collection_name(), delete=True)
