#!/usr/bin/env python
'''
Created on 13.09.2012

@author: unax
'''

DATABASES_NOSQL = {
    'mongoengine' : {
    'NAME'  : 'testbase',
    'USER'  : 'root',
    'PASSWORD': '****',
    'HOST'  : 'dbhost',
    'PORT'  : 27017, },
}

from mongoengine import connect

connect(DATABASES_NOSQL['mongoengine'].get('NAME'),
        username=DATABASES_NOSQL['mongoengine'].get('USER'),
        password=DATABASES_NOSQL['mongoengine'].get('PASSWORD'),
        host=DATABASES_NOSQL['mongoengine'].get('HOST'),
        port=DATABASES_NOSQL['mongoengine'].get('PORT') )

from IPython.frontend.terminal.embed import InteractiveShellEmbed
IPShell = InteractiveShellEmbed(user_ns={})
IPShell()
