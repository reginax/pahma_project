__author__ = 'jblowe'

from django.conf.urls import patterns, url
from shelvedimages import views

urlpatterns = patterns('',
                       # ex: /imageserver/blobs/5dbc3c43-b765-4c10-9d5d/derivatives/Medium/content
                       url(r'^stats', views.stats, name='stats'),
                       url(r'^(?P<image>.+)$', views.get_image, name='get_image'),
                       )