__author__ = 'jblowe'

from django.conf.urls import patterns, url
from uploadmedia import views

urlpatterns = patterns('',
                       url(r'^uploadfiles', views.uploadfiles, name='uploadfiles'),
                       url(r'^showqueue', views.showqueue, name='showqueue'),
                       url(r'^showresults/(?P<filename>[\w\-\.]+)$', views.showresults, name='showresults'),
                       #url(r'createmedia', views.createmedia, name='createmedia'),
                       )
