__author__ = 'jblowe'

import os
import re
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

from operator import itemgetter

# the following code attempts to find and import the best...
try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring

    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree

        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree

            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree

                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")

from common import cspace
from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()
TITLE = 'Image Browser'


@login_required()
def images(request):
    """
    takes two parameters pgNum and pgSz, retrieves XML via service call, parses the XML to get
    blob and other info, builds a page to retrieve thumbnails of all images in the set.

    NB: currently the target server for the links is hardcoded here and in the showImages.html template.

    :param request: two parameters to pass to CSpace: pgNum and pgSz
    :return: page of images
    """
    if 'pgNum' in request.GET and request.GET['pgNum']:
        elapsedtime = time.time()
        pgSz = request.GET['pgSz']
        pgNum = request.GET['pgNum']
        # do search
        connection = cspace.connection.create_connection(config, request.user)
        (url, data, statusCode) = connection.make_get_request(
            'cspace-services/%s?pgNum=%s&pgSz=%s&wf_deleted=false' % ('media', pgNum, pgSz))
        #...collectionobjects?pgNum=%27orchid%27&wf_deleted=false
        cspaceXML = fromstring(data)
        items = cspaceXML.findall('.//list-item')
        count = cspaceXML.find('.//totalItems')
        count = count.text
        results = []
        for i in items:
            r = []
            csid = i.find('.//csid')
            csid = csid.text
            blobCsid = i.find('.//blobCsid')
            try:
                blobCsid = blobCsid.text
            except:
                blobCsid = '0000'
            objectNumber = i.find('.//identificationNumber')
            try:
                objectNumber = objectNumber.text
            except:
                objectNumber = '0000'
            # hardcoded here for now, should eventually get these from the authentication backend
            # but tenant is not even stored there...
            hostname = 'pahma.cspace.berkeley.edu'
            tenant = 'pahma'
            link = 'http://%s:8180/collectionspace/ui/%s/html/media.html?csid=%s' % (hostname, tenant, csid)
            r.append(link)
            r.append(objectNumber)
            r.append(blobCsid)
            results.append(r)
        elapsedtime = time.time() - elapsedtime
        return render(request, 'showImages.html',
                      {'results': results, 'pgNum': pgNum, 'count': count, 'url': url, 'pgSz': pgSz,
                       'title': TITLE, 'time': '%8.2f' % elapsedtime})

    else:
        return render(request, 'showImages.html', {'title': TITLE, 'pgNum': 10, 'pgSz': 20})
