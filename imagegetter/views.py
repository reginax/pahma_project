__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from common import cspace
from cspace_django_site.main import cspace_django_site

from os import path
from ConfigParser import NoOptionError
import urllib2
import ConfigParser
import time
import solr
import base64


s = solr.SolrConnection(url='http://localhost:8983/solr/images')


TITLE = 'Caching Image Server Stats'

#@login_required()
def stats(request):
    elapsedtime = time.time()

    response = s.query('*:*')
    count = response._numFound
    return render(request, 'imagestats.html', {'title': TITLE, 'count': count})

#@login_required()
def get_image(request, image):

    elapsedtime = time.time()
    image = str(image)
    for i in range(3):
        try:
            response = s.query('csid:%s' % image)
            if response._numFound > 0:
                results = response.results
                blob = base64.b64decode(results[0]['blob'])
                print "%6.3f second, retrieved from cache :: %s" % (time.time() - elapsedtime, image)
                return HttpResponse(blob, mimetype='image/jpeg', status=200)
            #else:
            #    return HttpResponse(status=404)
        except:
            time.sleep(1)
            print "%6.3f seconds, pass %s : cache search failed for %s" % (time.time() - elapsedtime, i, image)

    return HttpResponse(status=200)