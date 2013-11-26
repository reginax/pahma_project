__author__ = 'jblowe'

from django.conf.urls import patterns, url
from uploadmedia import views

urlpatterns = patterns('',
                       url(r'^$', views.uploadfiles, name='uploadfiles'),
                       #url(r'createmedia', views.createmedia, name='createmedia'),
                       )
