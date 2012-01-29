'''
Created on 24.01.2012

@author: unax
'''
from django.http import HttpResponse
from models import TestModelList, TestModelObj, TestModelRef
from random import Random
from main import run_test_get, run_test_list, run_test_get_reference, run_test_list_reference

def main_page(request):
    return HttpResponse("""<h2>Tests for mongoengine_rediscache</h2>
    <ul>
    <li><a href="/create/2000">Create test collections (4000 objects of)</a></li>
    <p><b>Run tests. For pure experimentation, run each test more than once.</b></p>
    <li><a href="/test_get">Getting objects (TestModelObj.objects.get)</a></li>
    <li><a href="/test_list">Getting objects list (test for CachedQuerySet with any variants of filter(..) and order_by()</a></li>
    <li><a href="/test_get_reference">Getting objects from reference field (ReferenceFieldCached(Document))</a></li>
    <li><a href="/test_list_reference">Getting list of reference objects (ListFieldCached( ReferenceField(Document) ))</a></li>
    </ul>""")

def test_get(request):
    html='<p>Getting object</p>'
    
    html+='<ul><b>Test with used cache:</b> %s</ul>' % run_test_get(15000,True)
    html+='<ul><b>Test without cached:</b> %s</ul>'  % run_test_get(15000,False)
    
    return HttpResponse(html)

def test_list(request):
    html='<p>Select list</p>'

    html+='<ul><b>Test with used cache:</b> %s</ul>' % run_test_list(300,True)
    html+='<ul><b>Test without cached:</b> %s</ul>'  % run_test_list(300,False)
    
    return HttpResponse(html)


def test_get_reference(request):
    html='<p>Get reference object</p>'

    html+='<ul><b>Test with used cache:</b> %s</ul>' % run_test_get_reference(15000,True)
    html+='<ul><b>Test without cached:</b> %s</ul>'  % run_test_get_reference(15000,False)
    
    return HttpResponse(html)

def test_list_reference(request):
    html='<p>Get reference list</p>'

    html+='<ul><b>Test with used cache:</b> %s</ul>' % run_test_list_reference(10000,True)
    html+='<ul><b>Test without cached:</b> %s</ul>'  % run_test_list_reference(10000,False)
    
    return HttpResponse(html)

def create_models(request, count_models):
    count_models=int(count_models)
    
    rand=Random()
    
    rand_hextext=lambda rand: "".join([ rand.choice('0123456789abcdef') for i in range(rand.randint(8,16)) ])
    rand_hexname=lambda rand: "".join([ rand.choice('_abcdef') for i in range(rand.randint(2,4)) ])
    
    nums=[]
    all=0
    for i in range(count_models):
        all+=1
        n=rand.randint(0,1000000)
        nums.append(n)
        TestModelObj(num=n,
                    name=rand_hexname(rand),
                    text=rand_hextext(rand)).save()

    for i in range(count_models/2):
        all+=1
        TestModelRef(num=rand.randint(0,1000000),
                     model=TestModelObj.objects(num=rand.choice(nums))[0],
                     name=rand_hexname(rand)).save()
    
    for i in range(count_models/2):
        all+=1
        TestModelList(num=rand.randint(0,1000000),
                     models=TestModelObj.objects.filter(num__in= [ rand.choice(nums) for i in range( rand.randint(1,8) ) ]),
                     name=rand_hexname(rand)).save()
    return HttpResponse('Created %d models' % all)