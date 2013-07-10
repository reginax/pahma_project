from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views

admin.autodiscover()

#
# Initialize our web site -things like our AuthN backend need to be initialized.
#
from main import cspace_django_site

cspace_django_site.initialize()

urlpatterns = patterns('',
                       #  Examples:
                       #  url(r'^$', 'cspace_django_site.views.home', name='home'),
                       #  url(r'^cspace_django_site/', include('cspace_django_site.foo.urls')),

                       #  Uncomment the admin/doc line below to enable admin documentation:
                       #  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'hello.views.home', name='home'),
                       url(r'^service/', include('service.urls')),
                       url(r'^landing/', include('landing.urls')),
                       url(r'^accounts/login/$', views.login, name='login'),
                       url(r'^accounts/logout/$', views.logout_then_login, name='logout'),
                       url(r'^ireports/', include('ireports.urls', namespace='ireports')),
                       url(r'^imagebrowser/', include('imagebrowser.urls', namespace='imagebrowser')),
                       url(r'^imageserver/', include('imageserver.urls', namespace='imageserver')),
#                       url(r'^solrproxy/', include('solrproxy.urls', namespace='solrproxy')),
                       url(r'^solrapi/', include('solrapi.urls', namespace='solrapi')),
                       url(r'^search/', include('search.urls', namespace='search')),
                       url(r'^advsearch/', include('advsearch.urls', namespace='advsearch')),
                       url(r'^experiment/', include('experiment.urls', namespace='experiment')),
                       url(r'^autosuggest', include('autosuggest.urls', namespace='autosuggest')),
                       )
