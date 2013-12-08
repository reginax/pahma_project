import csv
import sys
import codecs

from cswaUtils import *
from cswaDB import getCSID

def mediaPayload(f):
    payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="media">
<ns2:media_common xmlns:ns2="http://collectionspace.org/services/media" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<blobCsid>%s</blobCsid>
<rightsHolder>%s</rightsHolder>
<creator>%s</creator>
<title>Media record</title>
<description>Contributors: %s</description>
<languageList>
<language>urn:cspace:pahma.cspace.berkeley.edu:vocabularies:name(languages):item:name(eng)'English'</language>
</languageList>
<identificationNumber>%s</identificationNumber>
</ns2:media_common>
<ns2:media_pahma xmlns:ns2="http://collectionspace.org/services/media/local/pahma" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<approvedForWeb>true</approvedForWeb>
<primaryDisplay>false</primaryDisplay>
</ns2:media_pahma>
</document>
"""
    payload = payload % (
        f['blobCsid'], f['rightsHolderRefname'], f['creator'],  f['contributor'], f['objectNumber'])
    return payload

def uploadmedia(mediaElements, config):

    realm = config.get('connect', 'realm')
    hostname = config.get('connect', 'hostname')
    username = config.get('connect', 'username')
    password = config.get('connect', 'password')

    #print relationsPayload(f)

    objectCSID = getCSID('objectnumber', mediaElements['objectnumber'], config)
    if objectCSID == []: 
        raise Exception("<span style='color:red'>Object Number not found: %s!</span>" % mediaElements['objectnumber'])
    else:
        objectCSID = objectCSID[0]
	mediaElements['objectCSID'] = objectCSID
        print "<br>object %s, csid: %s" % (mediaElements['objectnumber'],mediaElements['objectCSID'])

    updateItems = {'objectStatus': 'found',
          'subjectCsid': '',
          'objectCsid': mediaElements['objectCSID'],
          'objectNumber': mediaElements['objectnumber'],
          'blobCsid': mediaElements['blobCSID'],
          'rightsHolderRefname': mediaElements['rightsholder'],
          'contributor': mediaElements['contributor'],
          'creator': mediaElements['creator'],
          'mediaDate': mediaElements['date'],
          }

    uri = 'media'

    print "<br>posting to media REST API..."
    payload = mediaPayload(updateItems)
    (url, data, mediaCSID, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
    print 'got mediacsid', mediaCSID, '. elapsedtime', elapsedtime
    mediaElements['mediaCSID'] = mediaCSID
    print "media REST API post succeeded..."

    # now relate media record to collection object

    uri = 'relations'
    
    print "<br>posting media2obj to relations REST API..."
    
    updateItems['objectCsid'] = objectCSID
    updateItems['subjectCsid'] = mediaCSID
    # "urn:cspace:pahma.cspace.berkeley.edu:media:id(%s)" % mediaCSID
    
    updateItems['objectDocumentType'] = 'CollectionObject'
    updateItems['subjectDocumentType'] = 'Media'
    
    payload = relationsPayload(updateItems)
    (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
    print 'got relation csid', csid, '. elapsedtime', elapsedtime
    mediaElements['media2objCSID'] = csid
    print "relations REST API post succeeded..."

    # reverse the roles
    print "<br>posting obj2media to relations REST API..."
    temp = updateItems['objectCsid']
    updateItems['objectCsid'] = updateItems['subjectCsid']
    updateItems['subjectCsid'] = temp
    updateItems['objectDocumentType'] = 'Media'
    updateItems['subjectDocumentType'] = 'CollectionObject'
    payload = relationsPayload(updateItems)
    (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
    print 'got relation csid', csid, '. elapsedtime', elapsedtime
    mediaElements['obj2mediaCSID'] = csid
    print "relations REST API post succeeded..."

    print "<h3>Done w update!</h3>"
    return mediaElements


def getRecords(rawFile):
    try:
        records = []
        #csvfile = csv.reader(codecs.open(rawFile,'rb','utf-8'),delimiter="\t")
        csvfile = csv.reader(open(rawFile,'rb'),delimiter="|")
        for row, values in enumerate(csvfile):
            records.append(values)
        return records,len(values)
    except:
        raise

if __name__ == "__main__":


    form = {'webapp': 'uploadmediaDev'}
    config = getConfig(form)

    records,columns = getRecords(sys.argv[1])
    print '%s columns and %s lines found in file %s' % (columns,len(records),sys.argv[1])
    outputFile = sys.argv[1].replace('.step2.csv','.step3.csv')
    outputfh = csv.writer(open(outputFile,'wb'),delimiter="\t")


    for i, r in enumerate(records):

        mediaElements = {}
        for v1,v2 in enumerate('name size objectnumber blobCSID date creator contributor rightsholder fullpathtofile'.split(' ')):
            mediaElements[v2] = r[v1]
        #print mediaElements
        mediaElements = uploadmedia(mediaElements,config)
        r.append(mediaElements['mediaCSID'])
        outputfh.writerow(r)

