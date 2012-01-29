'''
Created on 25.01.2012

@author: unax
'''

from random import Random
import time

def run_test_get( n=1000, use_cache=True ):
    if use_cache:
        from models import TestModelObj
    else:
        from nocache_tests.models import TestModelObj
    
    all_pk_mobj= [ str(m.pk) for m in TestModelObj.objects() ]
    rand=Random()
    sum=0
    start_time=time.time()
    for i in range(n):
        new_obj=TestModelObj.objects.get(pk= rand.choice(all_pk_mobj) )
        sum+=new_obj.num
    end_time=time.time()-start_time
    
    return "<p>Count operations: %d</p><p>Time operations: %s</p>" % (n, str(end_time))
    

def run_test_list( n=100, use_cache=True ):
    if use_cache:
        from models import TestModelObj
    else:
        from nocache_tests.models import TestModelObj
    obj_count=0
    from datetime import datetime
    dt=datetime(1986,11,22,7,15)
    rand=Random()
    rand_hexname=lambda rand: "".join([ rand.choice('abcdef') for i in range(2) ])
    start_time=time.time()
    m=0
    for i in range(n):
        r=rand.randint(1, 15)
        if rand.randint(1, 10)>5:
            new_list=TestModelObj.objects.filter(create_date__gt=dt)
        else:
            new_list=TestModelObj.objects()
        if r>12:
            new_list.filter( num__lt = 500000 ).filter( text__contains = rand_hexname(rand) ).order_by("num")
        elif r>9:
            new_list.filter( text__contains = rand_hexname(rand) ).order_by("num")
        elif r>6:
            new_list.filter( name__contains = rand_hexname(rand) ).order_by("-name")
        elif r>3:
            new_list.filter( num__lt = 500000 ).order_by("-name")
        else:
            new_list.filter( num__gt = 500000 ).order_by("-name")
        
        if use_cache:
            new_list=new_list.cache
        
        if new_list.count()>0:
            m+=1
            sum=0
            for obj in new_list:
                sum+=obj.num
                obj_count+=1
            
    end_time=time.time()-start_time
    
    return "<p>Count operations: %d</p><p>Object count: %d</p><p>Time operations: %s</p><p>Average list length: %d</p>" % (n, obj_count, str(end_time), int(obj_count/m))

def run_test_get_reference( n=1000, use_cache=True ):
    if use_cache:
        from models import TestModelRef
    else:
        from nocache_tests.models import TestModelRef
    all_pk_mobj= [ str(m.pk) for m in TestModelRef.objects() ]
    rand=Random()
    sum=0
    start_time=time.time()
    for i in range(n):
        new_obj=TestModelRef.objects.get(pk=rand.choice(all_pk_mobj) )
        ref_obj=new_obj.model
        sum+=ref_obj.num
    end_time=time.time()-start_time
    
    return "<p>Objects count: %d</p><p>Time operations: %s</p>" % (n*2, str(end_time))

def run_test_list_reference( n=1000, use_cache=True ):
    if use_cache:
        from models import TestModelList
    else:
        from nocache_tests.models import TestModelList
    all_pk_mobj= [ str(m.pk) for m in TestModelList.objects() ]
    rand=Random()
    sum=0
    obj_count=0
    m=0
    start_time=time.time()
    for i in range(n):
        new_obj=TestModelList.objects.get(pk=rand.choice(all_pk_mobj) )
        sum=0
        for obj in new_obj.models:
            sum+=obj.num
            m+=1
        if sum>0:
            obj_count+=1
    end_time=time.time()-start_time
    
    return "<p>Count objects in reference list: %d</p><p>Time operations: %s</p><p>Average list length: %d</p>" % (m, str(end_time), int(m/obj_count))
