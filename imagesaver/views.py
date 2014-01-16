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


TITLE = 'Image Saver'

#@login_required()
def save_image(request, image):
    #config = cspace_django_site.getConfig()
    #connection = cspace.connection.create_connection(config, request.user)
    #(url, data, statusCode) = connection.make_get_request('cspace-services/%s' % image)
    #return HttpResponse(data, mimetype='image/jpeg')

    elapsedtime = time.time()
    image = str(image)

    realm = 'org.collectionspace.services'
    hostname = 'pahma.cspace.berkeley.edu'
    protocol = 'http'
    port = '8180'

    username = 'import@pahma.cspace.berkeley.edu'
    password = 'xxxxxx'

    server = protocol + "://" + hostname + ":" + port
    passman = urllib2.HTTPPasswordMgr()
    passman.add_password(realm, server, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    url = "%s/cspace-services/%s" % (server, image)

    try:
        f = urllib2.urlopen(url)
        blob = f.read()
        print "%6.3f second, retrieved from CSpace :: %s" % (time.time() - elapsedtime, image)
        elapsedtime = time.time()
    except urllib2.HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        raise
    except urllib2.URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        raise
    else:
        # add a document to the index
        try:
            s.add(csid=image, blob=base64.b64encode(blob), date_loaded='NOW' )
            s.commit()
            print "%6.3f second, saved to cache from CSpace :: %s" % (time.time() - elapsedtime, image)
            elapsedtime = time.time()
        except:
            print "%6.3f second, failed to add %s to cache" % (time.time() - elapsedtime, image)
        print "%6.3f second, returning now cached imaged :: %s" % (time.time() - elapsedtime, image)
        return HttpResponse(blob, mimetype='image/jpeg', status=200)
