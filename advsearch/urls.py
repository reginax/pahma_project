__author__ = 'jblowe'

from django.conf.urls import patterns, url
from advsearch import views

urlpatterns = patterns('',
                       url(r'^$', views.search, name='search'),
                       )
