__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import re

#parms = {'kw': ['orchid', 'true', 'a keyword search value, please', 'Keyword']}
#parms = {'determination': ['Allium hyalinum Curran', 'true', '', 'taxon'],
#    'object Number': ['UC903060', 'true', '', 'collectionobjects_common%3AobjectNumber']}
parms = {
    #'determination': ['Allium hyalinum Curran', 'true', '', 'collectionobjects_ucjeps%3Ataxon', ''],
    #'field collection country': ['Peru', 'true', '', 'collectionobjects_ucjeps%3AfieldLocCountry', ''],
    'field location verbatim': ['', 'true', '', 'collectionobjects_pahma%3Apahmafieldlocverbatim', ''],
    'field collector': ['Kroeber', 'true', '', 'collectionobjects_common%3AfieldCollectors', ''],
    'object Number': ['', 'true', '', 'collectionobjects_common%3AobjectNumber', '']
}
#from operator import itemgetter

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

from os import path
from common import cspace
from cspace_django_site import settings

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'advsearch.cfg')
AUTOSUGGESTURL = config.get('advsearch', 'AUTOSUGGESTURL')
TITLE = 'Advanced Search'


@login_required()
def search(request):
    if request.method == 'POST':
        search_form = forms.Form(request.POST)
        if search_form.is_valid():
            results = []
            # do search
            queryterms = []
            for p in request.POST:
                if p == 'csrfmiddlewaretoken': continue
                if not request.POST[p]: continue
                queryterms.append('%s%%20ILIKE%%20%%27%%25%s%%25%%27' % (parms[p][3], request.POST[p]))
            querystring = '?as=' + '%20AND%20'.join(queryterms)
            print queryterms
            connection = cspace.connection.create_connection(config, request.user)
            uri = 'cspace-services/%s%s&wf_deleted%%3Dfalse' % ('collectionobjects', querystring)
            # e.g. collectionobjects?kw=%27orchid%27&wf_deleted=false
            (url, data, statusCode) = connection.make_get_request(uri)
            try:
                cspaceXML = fromstring(data)
                items = cspaceXML.findall('.//list-item')
            except:
                items = []
            results = []
            hostname = 'pahma-dev.cspace.berkeley.edu'
            tenant = 'pahma'
            for i in items:
                r = []
                csid = i.find('.//csid')
                csid = csid.text
                objectNumber = i.find('.//objectNumber')
                objectNumber = objectNumber.text
                link = 'http://%s:8180/collectionspace/ui/%s/html/cataloging.html?csid=%s' % (hostname, tenant, csid)
                r.append(link)
                r.append(objectNumber)
                r2 = []
                for field in ['taxon', 'objectName']:
                    e = i.find('.//%s' % field)
                    e = '' if e is None else e.text
                    e = re.sub(r"^.*\)'(.*)'$", "\\1", e)
                    r2.append(e)
                    #for field in ['objectNumber','objectName','briefDescription','computedCurrentLocation']:
                r.append(r2)
                results.append(r)
            zeroResults = True if len(results) == 0 else False
            return render_to_response('search.html',
                                      {'labels': 'Object Name|Taxonomic Name'.split('|'),
                                       'AUTOSUGGESTURL': AUTOSUGGESTURL,
                                       'results': results, 'zeroResults': zeroResults,
                                       'form': search_form, 'url': url, 'title': TITLE},
                                      context_instance=RequestContext(request))
    else:
        search_form = forms.Form()
        for p in parms:
            if str(parms[p][1]) == 'false':
                search_form.fields[p] = forms.CharField(initial=parms[p][0], widget=forms.widgets.HiddenInput(),
                                                        required=True)
            else:
                search_form.fields[p] = forms.CharField(initial=parms[p][0], help_text=parms[p][2], required=True)

    return render_to_response('search.html',
                              {'form': search_form, 'zeroResults': False, 'title': TITLE},
                              context_instance=RequestContext(request))
