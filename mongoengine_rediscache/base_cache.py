# -*- coding: utf-8 -*-

import cPickle as pickle
import logging
import redis
from .config import LazySettings, DEFAULT_LOGGER
from functools import wraps
from hashlib import md5 as md5_constructor

DEFAULT_TIMEOUT = 60


class BaseCache(object):
    def cached(self, extra=None, timeout=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                md5 = md5_constructor()
                md5.update('{0}.{1}'.format(func.__module__, func.__name__))
                if extra:
                    md5.update(str(extra))
                if args:
                    md5.update(repr(args))
                if kwargs:
                    md5.update(repr(sorted(kwargs.items())))

                cache_key = 'c:{0}'.format(md5.hexdigest())

                try:
                    result = self.get(cache_key)
                except (ValueError, TypeError):
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
        if data:
            return pickle.loads(data)

    def pipeline_get(self, cache_key_list):
        if cache_key_list:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.get(key)
            data = pipe.execute()
            if data:
                return [pickle.loads(d) for d in data if d]
        return None

    def pipeline_delete(self, cache_key_list):
        if isinstance(cache_key_list, list) and len(cache_key_list) > 0:
            pipe = self.conn.pipeline()
            for key in cache_key_list:
                pipe.delete(key)
            data = pipe.execute()
            if data:
                return data
        return None

    def delete(self, cache_key):
        return self.conn.delete(cache_key)

    def set(self, cache_key, data, timeout=DEFAULT_TIMEOUT):
        if not self.conn:
            return
        assert isinstance(timeout, int)
        pickled_data = pickle.dumps(data)
        if timeout > 0:
            self.conn.setex(cache_key, pickled_data, timeout)
        else:
            self.conn.set(cache_key, pickled_data)

    def set_int(self, cache_key, data, timeout=DEFAULT_TIMEOUT):
        assert isinstance(timeout, int)
        self.conn.setex(cache_key, data, timeout)

    def get_int(self, cache_key):
        try:
            return int(self.conn.get(cache_key))
        except (AttributeError, TypeError, ValueError):
            return

    def incr(self, name, amount=1):
        self.conn.incr(name, amount)

    def flushall(self):
        if self.conn:
            self.conn.flushdb()
            return True
        return False

    def append_to_list(self, list_cache_key, data):
        self.conn.rpush(list_cache_key, data)

    def get_all_list(self, list_cache_key):
        return  self.conn.lrange(list_cache_key, 0, -1)


class LazyCache(object):
    __this = None
    __cache = None

    def setup(self):
        if not isinstance(self.__cache, RedisCache):
            conf = LazySettings().content.get('redis')
            conn = redis.Redis(**conf)
            self.__cache = RedisCache(conn)
            loger = logging.getLogger(DEFAULT_LOGGER)
            loger.debug('{0}: Cache connection is initialized'\
                .format(self.__class__.__name__))

    def __new__(cls):
        if cls.__this is None:
            cls.__this = super(LazyCache, cls).__new__(cls)
        return cls.__this

    def __getattr__(self, attr):
        try:
            value = self.__dict__[attr]
        except KeyError:
            self.setup()
            value = getattr(self.__cache, attr, None)
        return value

_internal_cache = LazyCache()
