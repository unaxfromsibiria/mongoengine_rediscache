from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url( r'^create/(?P<count_models>[0-9]{1,9})[/]{0,1}','tests.views.create_models', ),
    url( r'^test_get[/]{0,1}$', 'tests.views.test_get' ),
    url( r'^test_list[/]{0,1}$', 'tests.views.test_list' ),
    url( r'^test_get_reference[/]{0,1}$', 'tests.views.test_get_reference' ),
    url( r'^test_list_reference[/]{0,1}$', 'tests.views.test_list_reference' ),
    url( r'^admin[/]{0,1}', include(admin.site.urls)),
    url( r'^[/]{0,1}', 'tests.views.main_page' ),
)
