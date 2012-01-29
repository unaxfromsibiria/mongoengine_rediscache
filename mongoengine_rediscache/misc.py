'''
Created on 11.01.2012

@author: unax
'''
from mongoengine import Document
from mongoengine.queryset import QuerySet
from datetime import datetime
import hashlib
from pymongo.dbref import DBRef
from django.conf import settings
from re import _pattern_type

try:
    HASHED_NAME_ALWAYS=settings.MONGOENGINE_REDISCACHE.get('keyhashed')
except:
    HASHED_NAME_ALWAYS=False

class CacheNameMixer(object):
    __line=None
    
    def __init__(self, query_dict=None ):
        self.__line=self.__parse(query_dict)
    
    def __str__(self):
        return str(self.__line).replace(' ','')
    
    def __unicode__(self):
        return self.__line.replace(' ','')
    
    @property
    def hash(self):
        md5=hashlib.md5()
        md5.update(self.__line)
        return md5.hexdigest()
    
    @property
    def line(self):
        if HASHED_NAME_ALWAYS:
            return self.hash
        return str(self)
    
    @property
    def exist(self):
        return self.__line is not None and len(self.__line)>0

    def __create_str(self, query_obj ):
        if isinstance(query_obj, unicode) or isinstance(query_obj, str):
            return query_obj
        elif isinstance(query_obj, int):
            return str(query_obj)
        elif isinstance(query_obj, float):
            return str(query_obj)
        elif isinstance(query_obj, datetime):
            return query_obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(query_obj, Document):
            return str(query_obj.pk)
        elif isinstance(query_obj,  _pattern_type):
            return "regex(%s)" % query_obj.pattern
        elif isinstance(query_obj, dict):
            return self.__parse(query_obj)
        elif isinstance(query_obj, DBRef):
            return u"%s.id=%s" % ( query_obj.id, query_obj.collection )
        elif isinstance(query_obj, tuple):
            return u"(%s)" % (u",".join( [ self.__create_str(obj) for obj in query_obj ] ))          
        elif isinstance(query_obj, list) or isinstance(query_obj, QuerySet):
            return u"[%s]" % (u",".join( [ self.__create_str(obj) for obj in query_obj ] ))
        else:
            try:
                return str(query_obj)
            except:
                pass
        return u'unknown_type'

    def __parse(self, query_dict ): # query_dict is dict, list or tuple
        if isinstance(query_dict,dict) and query_dict.keys()>0:
            query_line=[]
            for key in query_dict:
                query_line.append(u'%s=%s' % (key, self.__create_str(query_dict.get(key))) )
            return u"|".join(query_line)
        elif isinstance(query_dict,tuple) or isinstance(query_dict,list):
            return u"(%s)" % ( u",".join( [ self.__create_str(key) for key in query_dict ] ) )
        return None

    def append(self, query_dict ):
        new_line=self.__parse(query_dict)
        if self.__line is not None and new_line is not None:
            self.__line += '|%s' % new_line
        elif new_line is not None:
            self.__line  = new_line
