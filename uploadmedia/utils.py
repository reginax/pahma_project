from PIL import Image
from PIL.ExifTags import TAGS
import csv
import codecs
import time, datetime
import logging

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)

tempimagedir = "/tmp/upload_cache/%s"
jobdir = "/tmp/upload_cache/%s"

#tempimagedir = "/tmp/%s"
#jobdir = "/tmp/%s"


def getDropdowns():
    return {
        'creators':
            {
                "Natasha Johnson": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'",
                "Elizabeth Minor": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7500)'Elizabeth Minor'"
            },
        'rightsholders':
            {
                "PAHMA": "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8107)'Phoebe A. Hearst Museum of Anthropology'",
                "Regents of UC": "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(6390)'University of California at Berkeley Regents'",
                "Academy of Art University": "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8544)'Academy of Art University'"
            }
    }


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
    # dummy function, for now
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
    destination = open(tempimagedir % f.name, 'wb+')
    with destination:
        for chunk in f.chunks():
            destination.write(chunk)
    destination.close()


def assignValue(defaultValue, override, imageData, exifvalue, refnameList):
    if override == 'always':
        return defaultValue, refnameList.get(defaultValue, defaultValue)
    elif exifvalue in imageData:
        imageValue = imageData[exifvalue]
        # a bit of cleanup
        imageValue = imageValue.strip()
        imageValue = imageValue.replace('"','')
        imageValue = imageValue.replace('\n','')
        imageValue = imageValue.replace('\r','')
        return imageValue, refnameList.get(imageValue, imageValue)
    elif override == 'ifblank':
        return defaultValue, refnameList.get(defaultValue, defaultValue)
    else:
        return '', ''


def getJobfile(jobnumber):
    return jobdir % jobnumber


def loginfo(infotype, line, request):
    logdata = ''
    #user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    logger.info('%s :: %s :: %s' % (infotype, line, logdata))

