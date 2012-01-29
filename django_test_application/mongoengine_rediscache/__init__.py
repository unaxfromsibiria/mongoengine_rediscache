# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import cPickle as pickle
from functools import wraps
from django.utils.hashcompat import md5_constructor
import os, time
import redis

try:
    redis_conf = settings.MONGOENGINE_REDISCACHE.get('redis')
except AttributeError:
    raise ImproperlyConfigured('Check MONGOENGINE_REDISCACHE in settings. ')

try:    redis_conn = redis.Redis(**redis_conf)
except: redis_conn = None

class _queryset_list(list):
    def __init__(self, anylist=None):
        if anylist is None:
            super(_queryset_list, self).__init__()
        else:
            super(_queryset_list, self).__init__(anylist)
    
    def count(self):
        return len(self)

class BaseCache(object):
    """
    Simple cache with time-based invalidation
    """
    def cached(self, extra=None, timeout=None):
        """
        A decorator for caching function calls
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                md5 = md5_constructor()
                md5.update('%s.%s' % (func.__module__, func.__name__))
                if extra is not None:
                    md5.update(str(extra))
                if args:
                    md5.update(repr(args))
                if kwargs:
                    md5.update(repr(sorted(kwargs.items())))

                cache_key = 'c:%s' % md5.hexdigest()

                try:
                    result = self.get(cache_key)
                except:
                    result = func(*args, **kwargs)
                    self.set(cache_key, result, timeout)
                return result
            return wrapper
        return decorator

class RedisCache(BaseCache):
    def __init__(self, conn):
        self.conn = conn

    def get(self, cache_key):
        if self.conn is None:
            return None
        data = self.conn.get(cache_key)
        if data is None:
            return None
        return pickle.loads(data)
    
    def pipeline_get(self, cache_key_list ):
        if isinstance(cache_key_list,list) and len(cache_key_list)>0:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.get(key)
            data=pipe.execute()
            if data is not None and len(data)>0:
                res=[]
                for d in data:
                    try: obj=pickle.loads(d)
                    except: obj=None
                    if obj is not None:
                        res.append(obj)
                return res
        return None
    
    def pipeline_delete(self, cache_key_list ):
        if isinstance(cache_key_list,list) and len(cache_key_list)>0:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.delete(key)
            data=pipe.execute()
            if data is not None and len(data)>0:
                return data
        return None
    
    def delete(self, cache_key ):
        return self.conn.delete(cache_key)

    def set(self, cache_key, data, timeout=None):
        if self.conn is None:
            return
        pickled_data = pickle.dumps(data)
        if timeout is not None:
            self.conn.setex(cache_key, pickled_data, timeout)
        else:
            self.conn.set(cache_key, pickled_data)

cache = RedisCache(redis_conn)
_internal_cache = RedisCache(redis_conn)

def install_signals(app):
    from mongoengine import signals
    for model_name in settings.MONGOENGINE_REDISCACHE.get('scheme'):
        try:
            exec('from %s.models import %s' % (app,model_name))             
            exec("signals.post_save.connect({0}.post_save, sender={0})".format(model_name) )
            exec("signals.post_delete.connect({0}.post_delete, sender={0})".format(model_name) )
        except:
            pass
