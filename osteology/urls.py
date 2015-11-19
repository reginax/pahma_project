__author__ = 'amywieliczka, jblowe'

from django.conf.urls import patterns, url
from osteology import views

urlpatterns = patterns('',
                       url(r'^/?$', views.direct, name='direct'),
                       url(r'^skeleton/$', views.skeleton, name='skeleton'),
                       url(r'^search/$', views.search, name='search'),
                       url(r'^search/(?P<fieldfile>[\w-]+)$', views.loadNewFields, name='loadNewFields'),
                       url(r'^results/$', views.retrieveResults, name='retrieveResults'),
                       url(r'^bmapper/$', views.bmapper, name='bmapper'),
                       url(r'^statistics/$', views.statistics, name='statistics'),
                       url(r'^csv/$', views.csv, name='csv'),
                       url(r'^gmapper/$', views.gmapper, name='gmapper'),
                       )
