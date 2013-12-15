__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django import forms
import time, datetime
from utils import getDropdowns, handle_uploaded_file, assignValue, getCSID, getNumber, get_exif, writeCsv, getJobfile, viewFile, getJoblist, loginfo, getQueue
import subprocess
import os,sys

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

    form = forms.Form(request)
    if request.POST:

        contributor = request.POST['contributor']
        overrideContributor = request.POST['overridecreator']

        creatorDisplayname = request.POST['creator']
        overrideCreator = request.POST['overridecreator']

        rightsholderDisplayname = request.POST['rightsholder']
        overrideRightsholder = request.POST['overriderightsholder']

        constants = {'creator': creatorDisplayname, 'contributor': contributor, 'rightsholder': rightsholderDisplayname}

        for lineno,afile in enumerate(request.FILES.getlist('imagefiles')):
            #print afile
            try:
                print "%s %s: %s %s (%s %s)" % ('id', lineno, 'name', afile.name, 'size', afile.size)
                im = get_exif(afile)
                objectnumber = getNumber(afile.name)
                #objectCSID = getCSID(objectnumber)
                creator, creatorRefname = assignValue(creatorDisplayname,overrideCreator,im,'Artist',dropdowns['creators'])
                contributor, dummy = assignValue(contributor,overrideContributor,im,'ImageDescription',{})
                rightsholder, rightsholderRefname = assignValue(rightsholderDisplayname,overrideRightsholder,im,'RightsHolder',dropdowns['rightsholders'])
                datetimedigitized, dummy = assignValue('','ifblank',im,'DateTimeDigitized',{})
                imageinfo = {'id': lineno, 'name': afile.name, 'size': afile.size,
                             'objectnumber': objectnumber,
                             #'objectCSID': objectCSID,
                             'date': datetimedigitized,
                             'creator': creatorRefname,
                             'contributor': contributor,
                             'rightsholder': rightsholderRefname,
                             'creatorDisplayname': creator,
                             'rightsholderDisplayname': rightsholder,
                             'contributorDisplayname': contributor
                }
                handle_uploaded_file(afile, imageinfo)
                images.append(imageinfo)
            except:
                #raise
                images.append({'name': afile.name, 'size': afile.size, 'error': 'problem extracting image metadata, not processed'})

        if len(images) > 0:
            jobnumber = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            jobinfo['jobnumber'] = jobnumber
            writeCsv(getJobfile(jobnumber)+'.step1.csv', images,
                     ['name', 'size', 'objectnumber', 'date', 'creator', 'contributor', 'rightsholder'])
            jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

            if 'createmedia' in request.POST:
                jobinfo['status'] = 'createmedia'
                env =  {"PATH": os.environ["PATH"] + ":/usr/local/share/django/pahma_project/uploadmedia" }
                loginfo('start', getJobfile(jobnumber), request)
                try:
                    retcode = subprocess.call(["/usr/local/share/django/pahma_project/uploadmedia/postblob.sh", getJobfile(jobnumber)])
                    if retcode < 0:
                        loginfo('process', jobnumber+" Child was terminated by signal %s" %  -retcode, request)
                    else:
                        loginfo('process', jobnumber+": Child returned %s" %  retcode, request)
                except OSError as e:
                    loginfo('error', "Execution failed: %s" % e, request)
                loginfo('finish', getJobfile(jobnumber), request)

            elif 'uploadmedia' in request.POST:
                jobinfo['status'] = 'uploadmedia'
            elif 'checkjobs' in request.POST:
                processedfiles = getQueue('processed')
            else:
                jobinfo['status'] = 'No status possible'

    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return render(request, 'uploadmedia.html',
                  {'title': TITLE, 'images': images, 'count': len(images), 'constants': constants, 'jobinfo': jobinfo,
                   'dropdowns': dropdowns, 'overrides': overrides, 'status': status, 'timestamp': timestamp, 'elapsedtime': '%8.2f' % elapsedtime})


#@login_required()
def showresults(request, filename):
    f = open(getJobfile(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


#@login_required()
def showqueue(request):
    elapsedtime = time.time()
    jobs,count = getJoblist()
    dropdowns = getDropdowns()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html',
                  {'dropdowns': dropdowns, 'overrides': overrides, 'timestamp': timestamp, 'elapsedtime': '%8.2f' % elapsedtime,
                   'status': status, 'title': TITLE, 'jobs': jobs, 'count': count})