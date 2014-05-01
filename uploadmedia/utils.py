from PIL import Image
from PIL.ExifTags import TAGS
import csv
import codecs
import time, datetime
import logging
from os import listdir
from xml.sax.saxutils import escape

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)

tempimagedir = "/tmp/upload_cache/%s"
jobdir = "/tmp/upload_cache/%s"


def getJobfile(jobnumber):
    return jobdir % jobnumber


def getJoblist():
    from os import listdir
    from os.path import isfile, join
    jobpath = jobdir % ''
    filelist = [ f for f in listdir(jobpath) if isfile(join(jobpath,f)) and ('.csv' in f or 'trace.log' in f) ]
    jobdict = {}
    for f in sorted(filelist):
        parts = f.split('.')
        if 'original' in parts[1]: continue
        elif 'processed' in parts[1]: status = 'complete'
        elif 'inprogress' in parts[1]: status = 'job started'
        elif 'step1' in parts[1]: status = 'pending'
        elif 'step2' in parts[1]: continue
        # we are in fact keeping the step2 files for now, but let's not show them...
        #elif 'step2' in parts[1]: status = 'blobs in progress'
        elif 'step3' in parts[1]: status = 'media in progress'
        elif 'trace' in parts[1]: status = 'run log'
        else: status = 'unknown'
        jobkey = parts[0]
        if not jobkey in jobdict: jobdict[jobkey] = []
        jobdict[jobkey].append([ f, status])
    joblist = [[ jobkey,False,jobdict[jobkey]] for jobkey in sorted(jobdict.keys(),reverse=True)]
    for ajob in joblist:
        ajob[1] = True
        for s in ajob[2] :
            if s[1] in ['complete','pending','job started']: ajob[1] = False
    count = len(joblist)
    return joblist[0:200], count


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
                "Alicja Egbert": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8683)'Alicja Egbert'",
                "Paolo Pellegatti": "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8020)'Paolo Pellegatti'"
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
    objectnumber = objectnumber.replace('.JPG','').replace('.jpg','')
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
                cell = str(item[x])
                cell = cell.strip()
                cell = cell.replace('"', '')
                cell = cell.replace('\n', '')
                cell = cell.replace('\r', '')
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
        imageValue = escape(imageValue)
        return imageValue, refnameList.get(imageValue, imageValue)
    elif override == 'ifblank':
        return defaultValue, refnameList.get(defaultValue, defaultValue)
    else:
        return '', ''

# this function not currently in use
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
            if i[0] == '#' : pass
        for l in [i.split('\t')[x] for x in [0,1,2,5]] :
            line += ('<td>%s</td>' % l)
            #for l in i.split('\t') : line += ('<td>%s</td>' % l)
            print '<tr>' + line  + '</tr>'

    except:
        print '<tr><td colspan="4">failed. sorry.</td></tr>'

    print '</table>'