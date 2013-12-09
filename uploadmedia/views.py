__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django import forms
import time, datetime
from utils import getDropdowns, handle_uploaded_file, assignValue, getCSID, getNumber, get_exif, writeCsv, getJobfile, loginfo
import subprocess
import os,sys

TITLE = 'Bulk Media Upload'

@login_required()
def uploadfiles(request):

    jobinfo = {}
    constants = {}
    images = []
    dropdowns = getDropdowns()

    form = forms.Form(request)
    if request.POST:

        contributor = request.POST['contributor']
        overrideContributor = request.POST['overridecreator']

        creatorDisplayname = request.POST['creator']
        overrideCreator = request.POST['overridecreator']
        defaultCreator = ''
        if creatorDisplayname in dropdowns['creators']:
            defaultCreator = dropdowns['creators'][creatorDisplayname]

        rightsholderDisplayname = request.POST['rightsholder']
        overrideRightsholder = request.POST['overriderightsholder']
        defaultRightsholder = ''
        if creatorDisplayname in dropdowns['rightsholders']:
            defaultRightsholder = dropdowns['rightsholders'][rightsholderDisplayname]

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
                loginfo('start', "finished job "+ getJobfile(jobnumber), request)
                #os.execlpe("bulkmediaupload.sh", "/tmp/upload_cache/%s" % jobnumber, env)
                #print os.system("bulkmediaupload.sh " + getJobfile(jobnumber))
                try:
                    retcode = subprocess.call("./bulkmediaupload.sh " + getJobfile(jobnumber), shell=True)
                    if retcode < 0:
                        loginfo('process', "Child was terminated by signal %s" %  -retcode, request)
                    else:
                        loginfo('process', "Child returned %s" %  retcode, request)
                except OSError as e:
                    loginfo('error', "Execution failed: %s" % e, request)
                loginfo('finish', "finished job "+ getJobfile(jobnumber), request)

            elif 'uploadmedia' in request.POST:
                jobinfo['status'] = 'uploadmedia'
            else:
                jobinfo['status'] = 'No status possible'

    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    overrides = [['ifblank', 'Overide only if blank'],
               ['always', 'Always Overide']]

    return render(request, 'uploadmedia.html',
                  {'title': TITLE, 'images': images, 'count': len(images), 'constants': constants, 'jobinfo': jobinfo,
                   'dropdowns': dropdowns, 'overrides': overrides, 'status': status, 'timestamp': timestamp})
