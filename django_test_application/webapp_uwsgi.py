# -*- coding: utf-8 -*-
import  os,sys
sys.path.append('/usr/local/lib/python2.7/dist-packages/django/')
sys.path.append('/data/web/cache_test/cachetest')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
