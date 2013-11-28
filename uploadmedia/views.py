__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.conf import settings
from django import forms
from PIL import Image
from PIL.ExifTags import TAGS
import csv
import codecs
import time, datetime

tempimagedir = "/tmp/upload_cache/%s"
jobdir = "/tmp/upload_cache/%s.csv"

#tempimagedir = "/tmp/%s"
#jobdir = "/tmp/%s.csv"


# following function take from stackoverflow...thanks!
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def getNumber(filename):
    objectnumber = filename.split('_')[0]
    return objectnumber


def getCSID(objectnumber):
    objectCSID = objectnumber
    return objectCSID


def writeCsv(filename, items, writeheader):
    filehandle = codecs.open(filename, 'w', 'utf-8')
    writer = csv.writer(filehandle, delimiter='\t')
    writer.writerow(writeheader)
    for item in items:
        row = []
        for x in writeheader:
            if x in item.keys():
                cell = item[x]
            else:
                cell = ''
            row.append(cell)
        writer.writerow(row)
    filehandle.close()


# following function borrowed from Django docs, w modifications
def handle_uploaded_file(f, imageinfo):
    with open(tempimagedir % f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required()
def uploadfiles(request):
    TITLE = 'Select Files to Upload'
    jobinfo = {}
    constants = {}
    images = []

    form = forms.Form(request)
    if request.POST:

        contributor = request.POST['contributor']
        creator = request.POST['creator']
        rightsholder = request.POST['rightsholder']
        constants = {'creator': creator, 'contributor': contributor, 'rightsholder': rightsholder}
        for id,afile in enumerate(request.FILES.getlist('imagefiles')):
            #print afile
            try:
                print "%s %s: %s %s (%s %s)" % ('id', id, 'name', afile.name, 'size', afile.size)
                im = get_exif(afile)
                objectnumber = getNumber(afile.name)
                objectCSID = getCSID(objectnumber)
                creator = creator if creator else im['Artist']
                contributor = contributor if contributor else im['ImageDescription']
                rightsholder = rightsholder if rightsholder else ''
                imageinfo = {'id': id, 'name': afile.name, 'size': afile.size, 'objectnumber': objectnumber, 'objectCSID': objectCSID,
                             'date': im['DateTimeDigitized'], 'creator': creator,
                             'contributor': contributor, 'rightsholder': rightsholder}
                images.append(imageinfo)
                #images.append([afile.name,afile.size])
                handle_uploaded_file(afile, imageinfo)
            except:
                images.append({'name': afile.name, 'size': afile.size, 'error': 'problem extracting image metadata, not processed'})

        if len(images) > 0:
            jobnumber = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            jobinfo['jobnumber'] = jobnumber
            writeCsv(jobdir % jobnumber, images,
                     ['name', 'size', 'objectnumber', 'objectCSID', 'date', 'contributor', 'rightsholder'])
            jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html',
                  {'title': TITLE, 'images': images, 'count': len(images), 'constants': constants, 'jobinfo': jobinfo,
                   'status': status, 'timestamp': timestamp})
