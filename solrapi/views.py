__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import time
import solr

TITLE = 'Solr-based Browser'


def getfacets(response):
    #facets = response.get('facet_counts').get('facet_fields')
    facets = response.facet_counts
    facets = facets['facet_fields']
    _facets = {}
    for key, values in facets.items():
        _v = []
        for k, v in values.items():
            _v.append((k, v))
        _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
    return _facets

@login_required()
def solrquery(request, solr_core):
    elapsedtime = time.time()
    # create a connection to a solr server
    s = solr.SolrConnection(url='http://localhost:8983/solr/%s' % solr_core)

    if 'kw' in request.GET:
        kw = request.GET['kw']
        try:
            pixonly = request.GET['pixonly']
        except:
            pixonly = None
            # do a search
        if kw == '': kw = '*'
        response = s.query('text:%s' % kw, facet='true', facet_field=['objectname_s', 'medium_s', 'culture_s'], rows=300,
                           facet_limit=20, facet_mincount=1)
        if kw == '*': kw = ''

        facetflds = getfacets(response)
        if pixonly:
            results = [r for r in response.results if r.has_key('blobs_ss')]
        else:
            results = response.results

        results = results[:36]

        elapsedtime = time.time() - elapsedtime
        return render(request, 'index.html',
                      {'time': '%8.3f' % elapsedtime, 'title': TITLE, 'count': response._numFound,
                       'results': results, 'kw': kw, 'pixonly': pixonly, 'facetsflds': facetflds, 'core': solr_core})

    else:
        return render(request, 'index.html', {'title': TITLE})