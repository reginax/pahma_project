__author__ = 'jblowe'

import os
import re
import time
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common.utils import doSearch, setConstants, loginfo
from common.appconfig import loadConfiguration, loadFields
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from os import path

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imaginator')

# read common config file
common = 'common'
prmz = loadConfiguration(common)
print 'Configuration for %s successfully read' % common
# read common config file
common = 'common'
prmz = loadConfiguration(common)
print 'Configuration for %s successfully read' % common

prmz.TITLE = 'Imaginator'
prmz.SOLRSERVER = config.get('imaginator', 'SOLRSERVER')
prmz.SOLRCORE = config.get('imaginator', 'SOLRCORE')
prmz.FIELDDEFINITIONS = config.get('imaginator', 'FIELDDEFINITIONS')

# on startup, setup this webapp layout...
prmz = loadFields(prmz.FIELDDEFINITIONS, prmz)

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('imaginator startup', '-', '%s | %s' % (prmz.SOLRSERVER, prmz.IMAGESERVER)))


@login_required()
def index(request):

    context = setConstants({}, prmz)

    # http://blog.mobileesp.com/
    # the middleware must be installed for the following to work...
    if request.is_phone:
        context['device'] = 'phone'
    elif request.is_tablet:
        context['device'] = 'tablet'
    else:
        context['device'] = 'other'

    if request.method == 'GET' and request.GET != {}:
        context['searchValues'] = request.GET

        if 'text' in request.GET:
            context['text'] = request.GET['text']
        if 'musno' in request.GET:
            context['musno'] = request.GET['musno']
            context['maxresults'] = 1
        if 'submit' in request.GET:
            context['maxresults'] = prmz.MAXRESULTS
            if "Metadata" in request.GET['submit']:
                context['resultType'] = 'metadata'
                context['displayType'] = 'full'
            elif "Images" in request.GET['submit']:
                context['resultType'] = 'images'
                context['pixonly'] = 'true'
                context['displayType'] = 'grid'
            elif "Lucky" in request.GET['submit']:
                context['resultType'] = 'metadata'
                context['maxresults'] = 1
        else:
            context['resultType'] = 'metadata'
        context['title'] = prmz.TITLE

        # do search
        loginfo(logger, 'start search', context, request)
        context = doSearch(context, prmz)

        return render(request, 'imagineImages.html', context)

    else:
        
        return render(request, 'imagineImages.html', context)
