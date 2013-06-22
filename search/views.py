__author__ = 'jblowe'

import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

from operator import itemgetter

# alas, there are many ways the XML parsing functionality might be installed.
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
TITLE = 'Keyword Search'


@login_required()
def search(request):
    if 'kw' in request.GET and request.GET['kw']:
        kw = request.GET['kw']
        # do search
        hostname = 'botgarden-dev.cspace.berkeley.edu'
        connection = cspace.connection.create_connection(config, request.user)
        (url, data, statusCode) = connection.make_get_request(
            'cspace-services/%s?kw=%s&&wf_deleted=false' % ('collectionobjects', kw))
        #...collectionobjects?kw=%27orchid%27&wf_deleted=false
        cspaceXML = fromstring(data)
        items = cspaceXML.findall('.//list-item')
        results = []
        for i in items:
            r = []
            csid = i.find('.//csid')
            csid = csid.text
            objectNumber = i.find('.//objectNumber')
            objectNumber = objectNumber.text
            hostname = 'pahma.cspace.berkeley.edu'
            tenant = 'pahma'
            link = 'http://%s:8180/collectionspace/ui/%s/html/cataloging.html?csid=%s' % (hostname, tenant, csid)
            r.append(link)
            r.append(objectNumber)
            r2 = []
            for field in ['taxon', 'objectName']:
                e = i.find('.//%s' % field)
                e = '' if e is None else e.text
                e = re.sub(r"^.*\)'(.*)'$", "\\1", e)
                r2.append(e)
            r.append(r2)
            results.append(r)
        return render(request, 'simplesearch.html',
                      {'results': results, 'kw': kw, 'labels': 'Object Number|Taxonomic Name'.split('|')})

    else:
        return render(request, 'simplesearch.html', {'title': TITLE})