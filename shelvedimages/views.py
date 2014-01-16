__author__ = 'jblowe'
# Add comment just to create a new diff between the most recent versions.
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
import shelve

TITLE = 'Caching Image Server Stats'

#@login_required()
def stats(request):
    elapsedtime = time.time()

    db = shelve.open('/tmp/db')
    count = len(db.keys())
    db.close()
    return render(request, 'stats.html', {'title': TITLE, 'count': count})

#@login_required()
def get_image(request, image):
    #config = cspace_django_site.getConfig()
    #connection = cspace.connection.create_connection(config, request.user)
    #(url, data, statusCode) = connection.make_get_request('cspace-services/%s' % image)
    #return HttpResponse(data, mimetype='image/jpeg')

    elapsedtime = time.time()
    image = str(image)

    # create a connection to a solr server
    s = solr.SolrConnection(url='http://localhost:8983/solr/images')
    if db.has_key(image):
        try:
            blob = db[image]
            db.close()
            elapsedtime = time.time() - elapsedtime
            print "%6.3f second, retrieved from cache :: %s" % (elapsedtime, image)
            return HttpResponse(blob, mimetype='image/jpeg', status=200)
        except:
            del db[image]
            pass
    else:
        db.close()

        #return HttpResponse(json.dumps(data), content_type='application/json', status=200)

        realm = 'org.collectionspace.services'
        # uri = 'cspace-services/accounts/0/accountperms'
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
        #print "<p>%s</p>" % url

        try:
            f = urllib2.urlopen(url)
            blob = f.read()
            elapsedtime = time.time() - elapsedtime
            print "%6.3f second, retrieved from CSpace :: %s" % (elapsedtime, image)
        except urllib2.HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            raise
        except urllib2.URLError, e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
            raise
        else:
            db = shelve.open('/tmp/db')
            db[image] = blob
            db.close()
            return HttpResponse(blob, mimetype='image/jpeg')
