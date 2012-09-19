# -*- coding: utf-8 -*-
from config import LazySettings
import cPickle as pickle
from functools import wraps
from hashlib import md5 as md5_constructor
import redis

DEFAULT_TIMEOUT = 600

class BaseCache(object):
    def cached(self, extra=None, timeout=None):
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
        data = self.conn.get(cache_key)
        if data is None:
            return None
        return pickle.loads(data)
    
    def pipeline_get(self, cache_key_list):
        if isinstance(cache_key_list, list) and len(cache_key_list) > 0:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.get(key)
            data = pipe.execute()
            if data is not None and len(data) > 0:
                res = []
                for d in data:
                    try: obj = pickle.loads(d)
                    except: obj = None
                    if obj is not None:
                        res.append(obj)
                return res
        return None
    
    def pipeline_delete(self, cache_key_list):
        if isinstance(cache_key_list, list) and len(cache_key_list) > 0:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.delete(key)
            data = pipe.execute()
            if data is not None and len(data) > 0:
                return data
        return None
    
    def delete(self, cache_key):
        return self.conn.delete(cache_key)

    def set(self, cache_key, data, timeout=DEFAULT_TIMEOUT):
        if self.conn is None:
            return
        pickled_data = pickle.dumps(data)
        if timeout is not None:
            self.conn.setex(cache_key, pickled_data, timeout)
        else:
            self.conn.set(cache_key, pickled_data)
    
    def flushall(self):
        if self.conn is None:
            return False
        try:    self.conn.flushdb()
        except: return False
        return True
    
    def append_to_list(self, list_cache_key, data):
        self.conn.rpush(list_cache_key, data)
    
    def get_all_list(self, list_cache_key):
        return  self.conn.lrange(list_cache_key, 0, -1)

class LazyCache(object):
    __this = None
    __cahe = None

    def __new__(cls):
        if not isinstance(cls.__cahe, RedisCache):
            # try connect
            try:     redis_conn = redis.Redis(**(LazySettings().content.get('redis')) )
            except:  redis_conn = None
            if redis_conn:
                # replace functional
                cls.__cahe          = RedisCache(redis_conn)
                cls.get             = cls.__cahe.get
                cls.pipeline_get    = cls.__cahe.pipeline_get
                cls.pipeline_delete = cls.__cahe.pipeline_delete
                cls.delete          = cls.__cahe.delete
                cls.append_to_list  = cls.__cahe.append_to_list
                cls.set             = cls.__cahe.set
                cls.flushall        = cls.__cahe.flushall
                cls.get_all_list    = cls.__cahe.get_all_list

        if cls.__this is None:
            cls.__this = super(LazyCache, cls).__new__(cls)
        return cls.__this

    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        LazyCache()

    def pipeline_get(self, *args, **kwargs):
        LazyCache()

    def pipeline_delete(self, *args, **kwargs):
        LazyCache()

    def delete(self, *args, **kwargs):
        LazyCache()

    def append_to_list(self, *args, **kwargs):
        LazyCache()

    def set(self, *args, **kwargs):
        LazyCache()

    def flushall(self, *args, **kwargs):
        LazyCache()

    def get_all_list(self, *args, **kwargs):
        LazyCache()

_internal_cache = LazyCache()
