from PIL import Image
from PIL.ExifTags import TAGS
import csv
import codecs
import time, datetime
import logging
from os import listdir

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)

tempimagedir = "/tmp/upload_cache/%s"
jobdir = "/tmp/upload_cache/%s"

tempimagedir = "/tmp/%s"
jobdir = "/tmp/%s"


def getJobfile(jobnumber):
    return jobdir % jobnumber


def getJoblist():
    from os import listdir
    from os.path import isfile, join
    mypath = jobdir % ''
    joblist = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and '.csv' in f ]
    joblist.sort(reverse=True)
    return joblist


def loginfo(infotype, line, request):
    logdata = ''
    #user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    logger.info('%s :: %s :: %s' % (infotype, line, logdata))


def getQueue(jobtypes):
    return [x for x in listdir(jobdir % '') if '%s.csv' % jobtypes in x]


def getDropdowns():
    return {
        'creators':
            {
                "Natasha Johnson": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'",
                "Elizabeth Minor": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7500)'Elizabeth Minor'"
            },
        'rightsholders':
            {
                "Phoebe A. Hearst Museum of Anthropology": "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8107)'Phoebe A. Hearst Museum of Anthropology'",
                "University of California at Berkeley Regents": "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(6390)'University of California at Berkeley Regents'"
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
        imageValue = imageValue.replace('"', '')
        imageValue = imageValue.replace('\n', '')
        imageValue = imageValue.replace('\r', '')
        return imageValue, refnameList.get(imageValue, imageValue)
    elif override == 'ifblank':
        return defaultValue, refnameList.get(defaultValue, defaultValue)
    else:
        return '', ''

def viewFile(logfilename,numtodisplay):

    print '<table width="100%">\n'
    print ('<tr>'+ (4 * '<th class="ncell">%s</td>') +'</tr>\n') % ('locationDate,objectNumber,objectStatus,handler'.split(','))
    try:
        file_handle = open(logfilename)
        file_size = file_handle.tell()
        file_handle.seek(max(file_size - 9*1024, 0))

        lastn = file_handle.read().splitlines()[-numtodisplay:]
        for i in lastn:
 	    i = i.replace('urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name','')
            line = ''
            if i[0] == '#' : continue
	    for l in [i.split('\t')[x] for x in [0,1,2,5]] : line += ('<td>%s</td>' % l)
	    #for l in i.split('\t') : line += ('<td>%s</td>' % l)
            print '<tr>' + line  + '</tr>'

    except:
	print '<tr><td colspan="4">failed. sorry.</td></tr>'

    print '</table>'