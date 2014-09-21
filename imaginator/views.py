__author__ = 'jblowe'

import os
import re
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from search.utils import doSearch, setConstants, loginfo
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from os import path

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imaginator')

MAXMARKERS = int(config.get('imaginator', 'MAXMARKERS'))
MAXRESULTS = int(config.get('imaginator', 'MAXRESULTS'))
MAXLONGRESULTS = int(config.get('imaginator', 'MAXLONGRESULTS'))
IMAGESERVER = config.get('imaginator', 'IMAGESERVER')
CSPACESERVER = config.get('imaginator', 'CSPACESERVER')
SOLRSERVER = config.get('imaginator', 'SOLRSERVER')
SOLRCORE = config.get('imaginator', 'SOLRCORE')
TITLE = config.get('imaginator', 'TITLE')
SUGGESTIONS = config.get('imaginator', 'SUGGESTIONS')
LAYOUT = config.get('imaginator', 'LAYOUT')


#@login_required()
def images(request):

    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}

        context = setConstants(context)

        context['text'] = request.GET['text']
        #context['pgNum'] = pgNum if 'pgNum' in context else '1'
        #context['url'] = url
        context['displayType'] = 'list'
        context['pixonly'] = 'true'
        context['title'] = TITLE

        # do search
        loginfo('start search', context, request)
        context = doSearch(SOLRSERVER, SOLRCORE, context)

        return render(request, 'imagineImages.html', context)

    else:
        return render(request, 'imagineImages.html', {'title': TITLE, 'pgNum': 10, 'maxresults': 20})
