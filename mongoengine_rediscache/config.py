'''
Created on 19.06.2012

@author: unax
'''
from django.conf import settings

def simple_scheme():
    data={}
    scheme=settings.MONGOENGINE_REDISCACHE.get('scheme')
    for model_location in scheme:
        data[model_location.split('.')[-1]]=scheme[model_location]
    return data

MONGOENGINE_REDISCACHE_SCHEME = simple_scheme()

def scheme_timelimit(model_name, request):
    scheme=MONGOENGINE_REDISCACHE_SCHEME.get(model_name)
    if scheme is None:
        return None
    timeout=scheme.get(request)
    if timeout is None:
        timeout=scheme.get('all')
    del scheme
    return timeout
