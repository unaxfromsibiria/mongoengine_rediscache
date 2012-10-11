# -*- coding: utf-8 -*-
'''
Created on 09.10.2012

@author: unax
'''

from random import Random
from datetime import datetime, timedelta
import time
import sys
rand = Random()

from models import Model1, Model2, Model3

def random_hex(size=rand.randint(8, 32)):
    return u"".join([ rand.choice('023456789abcdef') for i in range(size) ])

def random_date(interval=(datetime(2012, 10, 1), datetime(2012, 10, 3))):
    s = int((interval[1] - interval[0]).total_seconds())
    return interval[0] + timedelta(seconds=rand.randint(1, s - 1))
    
def create_models(n=10000, only=[1, 2, 3]):
    if 1 in only:
        print 'will be created %d Model1' % n
        for i in range(n):
            m = Model1(name=random_hex(),
                       volume=rand.randint(1, n),
                       created=random_date())
            m.save()
    
    k = Model1.objects().count()

    if 2 in only:
        print 'will be created %d Model2' % n
        
        for i in range(n):
            t = rand.randint(2, k - 2)
            m = Model2(name=random_hex(),
                       model1=Model1.objects()[t:t + 1][0],
                       count=rand.randint(1, n),
                       created=random_date())
            m.save()

    if 3 in only:
        print 'will be created %d Model3' % n
        for i in range(n):
            m = Model3(name=random_hex(),
                       model1=[],
                       count=rand.randint(1, n),
                       created=random_date())
            for j in range(rand.randint(1, 16)):
                t = rand.randint(2, k - 2)
                m.model1.append(Model1.objects()[t:t + 1][0])
            m.save()

def get_test(n=50000):
    pk_list = [ str(m.pk) for m in Model1.objects() ]
    # warmer
    for k in pk_list:
        m = Model1.objects.get(pk=k)

    print 'Get test (operations count: %d):' % n
    start_time = time.time()
    s = 0
    for i in range(n):
        k = rand.choice(pk_list)
        m = Model1.objects.get(pk=k)
        s += sys.getsizeof(m)
    
    print 'time: %s' % str(time.time() - start_time)
    print 'total lists size %s mb' % str(float(s)/float(1024**2))[0:5]

dates = [ random_date() for i in range(5) ]
val = [ rand.randint(4000,5000) for i in range(5) ]
chars = [ u"%s%s" % (rand.choice('023456789abcdef'),rand.choice('023456789abcdef')) for i in range(5) ]

def list_and_count_test(n=10000):
    pk_list = [ str(m.pk) for m in Model1.objects() ]
    # warmer
    for k in pk_list:
        m = Model1.objects.get(pk=k)

    m = 0
    s = 0
    print 'Count&List test (operations count: %d):' % n
    start_time = time.time()
    for i in range(n):
        models = Model1.objects(created__lt = rand.choice(dates))
        if rand.randint(0, 10) > 5:
            models.filter(volume__gt = rand.choice(val))
        if rand.randint(0, 10) > 5:
            models.filter(name__contains = rand.choice(chars))
        if models.count() > 0:
            models.limit(20)
            l = models.cache
            m += models.count()
            for obj in l:
                if obj.pk:
                    s += sys.getsizeof(obj)
    
    print 'time: %s' % str(time.time() - start_time)
    print 'object count: %d' % m
    print 'total lists size %s mb' % str(float(s)/float(1024**2))[0:5]

def reference_get_test(n=50000):
    # warmer
    pk_list = [ str(m.pk) for m in Model1.objects() ]
    for k in pk_list:
        m = Model1.objects.get(pk=k)
    pk_list = [ str(m.pk) for m in Model2.objects() ]
    for k in pk_list:
        m = Model2.objects.get(pk=k)

    print 'Reference get test (operations count: %d):' % n
    start_time = time.time()
    s = 0
    for i in range(n):
        k = rand.choice(pk_list)
        m = Model2.objects.get(pk=k)
        s += sys.getsizeof(m) + sys.getsizeof(m.model1)
    
    print 'time: %s' % str(time.time() - start_time)
    print 'total lists size %s mb' % str(float(s)/float(1024**2))[0:5]

def reference_list_test(n=1000):
    # warmer
    pk_list = [ str(m.pk) for m in Model1.objects() ]
    for k in pk_list:
        m = Model1.objects.get(pk=k)
    pk_list = [ str(m.pk) for m in Model3.objects() ]
    for k in pk_list:
        m = Model3.objects.get(pk=k)

    print 'Reference list test (operations count: %d):' % n
    start_time = time.time()
    s = 0
    for i in range(n):
        k = rand.choice(pk_list)
        m = Model3.objects.get(pk=k)
        s += sys.getsizeof(m)
        for m1 in m.model1:
            s += sys.getsizeof(m1)
    
    print 'time: %s' % str(time.time() - start_time)
    print 'total lists size %s mb' % str(float(s)/float(1024**2))[0:5]
