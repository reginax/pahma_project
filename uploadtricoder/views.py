__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
#from common.cspace import logged_in_or_basicauth
from django.shortcuts import render, HttpResponse, redirect
from django.core.servers.basehttp import FileWrapper
#from django.conf import settings
#from django import forms
import time, datetime
from utils import SERVERINFO, TITLE, POSTBLOBPATH, handle_uploaded_file, getCSID, get_tricoder_file, get_tricoder_filelist, loginfo, getQueue
import subprocess


class trcdr:  # empty class for tricoder metadata
    pass


def prepareFiles(request, validateonly):
    tricoder_fileinfo = {}
    tricoder_files = []
    for lineno, afile in enumerate(request.FILES.getlist('tricoderfiles')):
        # print afile
        try:
            print "%s %s: %s %s (%s %s)" % ('id', lineno, 'name', afile.name, 'size', afile.size)
            fileinfo = {'id': lineno, 'name': afile.name, 'size': afile.size, 'date': ''}
            if not validateonly:
                handle_uploaded_file(afile)
            tricoder_files.append(fileinfo)
        except:
            if not validateonly:
                # we still upload the file, anyway...
                handle_uploaded_file(afile)
            tricoder_files.append({'name': afile.name, 'size': afile.size,
                           'error': 'problem extracting image metadata, not processed'})

    if len(tricoder_files) > 0:
        tricoder_filenumber = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        tricoder_fileinfo['tricoder_filenumber'] = tricoder_filenumber
        tricoder_fileinfo['estimatedtime'] = '%8.1f' % (len(tricoder_files) * 10 / 60.0)

        if 'createtricoder' in request.POST:
            tricoder_fileinfo['status'] = 'createtricoder'
            if not validateonly:
                loginfo('start', get_tricoder_file(tricoder_filenumber), request)
                try:
                    retcode = subprocess.call(
                        [POSTBLOBPATH, get_tricoder_file(tricoder_filenumber)])
                    if retcode < 0:
                        loginfo('process', tricoder_filenumber + " Child was terminated by signal %s" % -retcode, request)
                    else:
                        loginfo('process', tricoder_filenumber + ": Child returned %s" % retcode, request)
                except OSError as e:
                    loginfo('error', "Execution failed: %s" % e, request)
                loginfo('finish', get_tricoder_file(tricoder_filenumber), request)

        elif 'uploadtricoder' in request.POST:
            tricoder_fileinfo['status'] = 'uploadtricoder'
        else:
            tricoder_fileinfo['status'] = 'No status possible'

    return tricoder_fileinfo, tricoder_files


def setConstants(request, trcdr):

    trcdr.validateonly = 'validateonly' in request.POST

    constants = {}

    return constants


@csrf_exempt
#@logged_in_or_basicauth()
def rest(request, action):
    elapsedtime = time.time()
    status = 'error' # assume murphy's law applies...

    if request.FILES:
        setConstants(request, trcdr)
        tricoder_fileinfo, tricoder_files = prepareFiles(request, trcdr.validateonly)
        status = 'ok' # OK, I guess it doesn't after all
    else:
        tricoder_fileinfo = {}
        tricoder_files = []
        status = 'no post seen' # OK, I guess it doesn't after all
        return HttpResponse(json.dumps({'status': status}))

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return HttpResponse(json.dumps(
        {'status': status, 'tricoder_files': tricoder_files, 'tricoder_fileinfo': tricoder_fileinfo, 'elapsedtime': '%8.2f' % elapsedtime}), content_type='text/json')


@login_required()
def uploadfiles(request):
    elapsedtime = time.time()
    status = 'up'
    constants = setConstants(request, trcdr)

    if request.POST:
        constants = setConstants(request, trcdr)
        tricoder_fileinfo, tricoder_files = prepareFiles(request, trcdr.validateonly)
    else:
        tricoder_fileinfo = {}
        tricoder_files = []
        constants = {}

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return render(request, 'uploadtricoder.html',
                  {'apptitle': TITLE, 'serverinfo': SERVERINFO, 'tricoder_files': tricoder_files, 'count': len(tricoder_files),
                   'constants': constants, 'tricoder_fileinfo': tricoder_fileinfo, 'validateonly': trcdr.validateonly,
                   'status': status, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime})


@login_required()
def checkfilename(request):
    elapsedtime = time.time()
    if 'filenames2check' in request.POST and request.POST['filenames2check'] != '':
        listoffilenames = request.POST['filenames2check']
        filenames = listoffilenames.split(' ')
        objectnumbers = [o for o in filenames]
    else:
        objectnumbers = []
        listoffilenames = ''
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadtricoder.html', {'filenames2check': listoffilenames,
                                                'objectnumbers': objectnumbers, 'timestamp': timestamp,
                                                'elapsedtime': '%8.2f' % elapsedtime,
                                                'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO})


@login_required()
def showresults(request, filename):
    f = open(get_tricoder_file(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    tricoder_files, errors, tricoder_filecount, errorcount = get_tricoder_filelist()
    if 'checkfiles' in request.POST:
        errors = None
    elif 'showerrors' in request.POST:
        tricoder_files = None
    else:
        tricoder_files = None
        errors = None
        count = 0
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadtricoder.html',
                  {'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime,
                   'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO, 'tricoder_files': tricoder_files, 'tricoder_filecount': tricoder_filecount,
                   'errors': errors, 'errorcount': errorcount})
