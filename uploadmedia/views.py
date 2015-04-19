__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django import forms
import time, datetime
from utils import SERVERINFO, getDropdowns, handle_uploaded_file, assignValue, getCSID, getNumber, get_exif, writeCsv, \
    getJobfile, getJoblist, loginfo, getQueue
import subprocess
import os, sys

TITLE = 'Bulk Media Upload'

overrides = [['ifblank', 'Overide only if blank'],
             ['always', 'Always Overide']]

@login_required()
def uploadfiles(request):
    jobinfo = {}
    constants = {}
    images = []
    dropdowns = getDropdowns()
    elapsedtime = time.time()
    status = 'up'
    validateonly = False

    form = forms.Form(request)
    if request.POST:

        validateonly = 'validateonly' in request.POST

        contributor = request.POST['contributor']
        overrideContributor = request.POST['overridecreator']

        creatorDisplayname = request.POST['creator']
        overrideCreator = request.POST['overridecreator']

        rightsholderDisplayname = request.POST['rightsholder']
        overrideRightsholder = request.POST['overriderightsholder']

        constants = {'creator': creatorDisplayname, 'contributor': contributor, 'rightsholder': rightsholderDisplayname}

        for lineno, afile in enumerate(request.FILES.getlist('imagefiles')):
            # print afile
            try:
                print "%s %s: %s %s (%s %s)" % ('id', lineno, 'name', afile.name, 'size', afile.size)
                im = get_exif(afile)
                filename, objectnumber, imagenumber = getNumber(afile.name)
                # objectCSID = getCSID(objectnumber)
                creator, creatorRefname = assignValue(creatorDisplayname, overrideCreator, im, 'Artist',
                                                      dropdowns['creators'])
                contributor, dummy = assignValue(contributor, overrideContributor, im, 'ImageDescription', {})
                rightsholder, rightsholderRefname = assignValue(rightsholderDisplayname, overrideRightsholder, im,
                                                                'RightsHolder', dropdowns['rightsholders'])
                datetimedigitized, dummy = assignValue('', 'ifblank', im, 'DateTimeDigitized', {})
                imageinfo = {'id': lineno, 'name': afile.name, 'size': afile.size,
                             'objectnumber': objectnumber,
                             'imagenumber': imagenumber,
                             #'objectCSID': objectCSID,
                             'date': datetimedigitized,
                             'creator': creatorRefname,
                             'contributor': contributor,
                             'rightsholder': rightsholderRefname,
                             'creatorDisplayname': creator,
                             'rightsholderDisplayname': rightsholder,
                             'contributorDisplayname': contributor
                }
                if not validateonly:
                    handle_uploaded_file(afile, imageinfo)
                images.append(imageinfo)
            except:
                if not validateonly:
                    # we still upload the file, anyway...
                    handle_uploaded_file(afile, imageinfo)
                images.append({'name': afile.name, 'size': afile.size,
                               'error': 'problem extracting image metadata, not processed'})

        if len(images) > 0:
            jobnumber = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            jobinfo['jobnumber'] = jobnumber

            if not validateonly:
                writeCsv(getJobfile(jobnumber) + '.step1.csv', images,
                         ['name', 'size', 'objectnumber', 'date', 'creator', 'contributor', 'rightsholder', 'imagenumber'])
            jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

            if 'createmedia' in request.POST:
                jobinfo['status'] = 'createmedia'
                if not validateonly:
                    loginfo('start', getJobfile(jobnumber), request)
                    try:
                        retcode = subprocess.call(
                            ["/usr/local/share/django/bampfa_project/uploadmedia/postblob.sh", getJobfile(jobnumber)])
                        if retcode < 0:
                            loginfo('process', jobnumber + " Child was terminated by signal %s" % -retcode, request)
                        else:
                            loginfo('process', jobnumber + ": Child returned %s" % retcode, request)
                    except OSError as e:
                        loginfo('error', "Execution failed: %s" % e, request)
                    loginfo('finish', getJobfile(jobnumber), request)

            elif 'uploadmedia' in request.POST:
                jobinfo['status'] = 'uploadmedia'
            else:
                jobinfo['status'] = 'No status possible'

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return render(request, 'uploadmedia.html',
                  {'title': TITLE, 'serverinfo': SERVERINFO, 'images': images, 'count': len(images),
                   'constants': constants, 'jobinfo': jobinfo, 'validateonly': validateonly,
                   'dropdowns': dropdowns, 'overrides': overrides, 'status': status, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime})


@login_required()
def checkfilename(request):
    elapsedtime = time.time()
    if 'filenames2check' in request.POST and request.POST['filenames2check'] != '':
        listoffilenames = request.POST['filenames2check']
        filenames = listoffilenames.split(' ')
        objectnumbers = [getNumber(o) for o in filenames]
    else:
        objectnumbers = []
        listoffilenames = ''
    dropdowns = getDropdowns()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html', {'filenames2check': listoffilenames,
                                                'objectnumbers': objectnumbers, 'dropdowns': dropdowns,
                                                'overrides': overrides, 'timestamp': timestamp,
                                                'elapsedtime': '%8.2f' % elapsedtime,
                                                'status': status, 'title': TITLE, 'serverinfo': SERVERINFO})


@login_required()
def showresults(request, filename):
    f = open(getJobfile(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    jobs, count = getJoblist()
    dropdowns = getDropdowns()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html',
                  {'dropdowns': dropdowns, 'overrides': overrides, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime,
                   'status': status, 'title': TITLE, 'serverinfo': SERVERINFO, 'jobs': jobs, 'count': count})