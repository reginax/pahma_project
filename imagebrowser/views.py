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

from publicsearch.utils import writeCsv, doSearch, setupGoogleMap, setupBMapper, setDisplayType, setConstants, loginfo

MAXMARKERS = 65
MAXRESULTS = 1000
MAXLONGRESULTS = 50
IMAGESERVER = 'https://pahma-dev.cspace.berkeley.edu/pahma_project/imageserver' # no final slash
SOLRSERVER = 'http://localhost:8983/solr'
SOLRCORE = 'pahma-metadata'

from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imagebrowser')

MAXMARKERS = config.get('imagebrowser', 'MAXMARKERS')
MAXRESULTS = config.get('imagebrowser', 'MAXRESULTS')
MAXLONGRESULTS = config.get('imagebrowser', 'MAXLONGRESULTS')
IMAGESERVER = config.get('imagebrowser', 'IMAGESERVER')


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
    #if 'keyword' in request.GET and request.GET['keyword']:
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}

        context = setConstants(context)
        loginfo('start search', context, request)

        maxresults = request.GET['maxresults']
        # do search
        context = doSearch(SOLRSERVER, SOLRCORE, context)
        context['imageserver'] = IMAGESERVER
        context['keyword'] = request.GET['keyword']
        #context['pgNum'] = pgNum if 'pgNum' in context else '1'
        #context['url'] = url
        context['maxresults'] = maxresults
        context['displayType'] = 'list'
        context['pixonly'] = 'true'
        context['title'] = TITLE

        return render(request, 'showImages.html', context)

    else:
        return render(request, 'showImages.html', {'title': TITLE, 'pgNum': 10, 'maxresults': 20})
