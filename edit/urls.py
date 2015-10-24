__author__ = 'jblowe'

from django.conf.urls import patterns, url
from edit import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<entity>[\w-]+)/?(?P<csid>[\w-]+)$', views.edit, name='edit'),
                       )
