'''
Created on 25.01.2012

@author: unax
'''

from datetime import datetime
from mongoengine import *

class TestModelObj(Document):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    text =  StringField(max_length=255, required=False )
    create_date = DateTimeField(default=datetime.now())

class TestModelList(Document):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    models = ListField( ReferenceField(TestModelObj) )
    
class TestModelRef(Document):
    num  =  IntField(default=0)
    name =  StringField(max_length=255, required=False )
    model = ReferenceField(TestModelObj)
