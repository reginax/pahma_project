__author__ = 'jblowe'

from django.conf.urls import patterns, url
from solrapi import views

urlpatterns = patterns('',
                       # ex: /solr/pahma
                       url(r'^(?P<solr_core>.+)$', views.solrquery, name='solr'),
                       )