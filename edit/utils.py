import re
import time, datetime
import csv
import solr
import cgi
import logging
from os import path

from common import cspace # we use the config file reading function
from cspace_django_site import settings

try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring
    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree
        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree
            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree
                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")

# global variables

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('toolbox startup', '-', '-'))

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'edit')
entities = config.get('info','entities')

from cspace_django_site.main import cspace_django_site
siteconfig = cspace_django_site.getConfig()


def loginfo(infotype, context, request):
    logdata = ''
    #user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    if 'count' in context:
        count = context['count']
    else:
        count = '-'
    if 'querystring' in context:
        logdata = context['querystring']
    if 'url' in context:
        logdata += ' :: %s' % context['url']
    logger.info('%s :: %s :: %s :: %s' % (infotype, count, username, logdata))


def setConstants(context):

    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    context['apptitle'] = 'Super Edit'

    return context


def getfromXML(element,xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*\)'(.*)'$", "\\1", result)
    return result

def doEdit(request,context):

    connection = cspace.connection.create_connection(siteconfig, request.user)
    (url, data, statusCode) = connection.make_get_request('cspace-services/%s/%s' % (context['entity'],context['csid']))
    if data is None:
        context['errormsg'] = 'No entity with this name found.'
    else:
        entityXML = fromstring(data)
        #elements = [csidElement.text for csidElement in entityXML.findall('.//csid')]
        items = []
        nochangeitems = []
        for child in entityXML.getiterator():
            if child.tag in 'tenantId scalarValuesComputed updatedAt workflowState createdBy createdAt refName uri updatedBy accountId screenName userId'.split(' '):
                if child.tag == 'scalarValuesComputed':
                    pass
                else:
                    nochangeitems.append( {'label': child.tag, 'default': child.text, 'style': 'width:150px'} )
            else:
                print child.tag
                if child.text:
                    items.append( {'label': child.tag, 'default': child.text, 'style': 'width:150px'} )

        context['items'] = items
        context['nochangeitems'] = nochangeitems

    return context

def getEntityList():
    return entities.split(',')


def getEmpty(request,context):

    # get a record of the required type, empty it out to make a template...
    # first, get a csid for a record of this type
    connection = cspace.connection.create_connection(siteconfig, request.user)
    (url, data, statusCode) = connection.make_get_request('cspace-services/%s' % context['entity'])
    root = etree.fromstring(data)
    # get the first
    csid = root.find('.//list-item/csid')
    csid = csid.text

    print 'csid %s' % csid
    # get the first item of this type
    (url, data, statusCode) = connection.make_get_request('cspace-services/%s' % context['entity'])
    xmlTemplate = etree.fromstring(data)
    # ns2:collectionspace_core
    core = xmlTemplate.find('.//{http://collectionspace.org/collectionspace_core/}collectionspace_core')
    tenantId = core.find('.//tenantId').text
    for c in sorted(core):
        if c.tag == 'refName' or c.tag == 'tenantId':
            pass
        else:
            core.remove(c)
    #xmlTemplate.remove(core)
    # ns2:account_permission
    perms = xmlTemplate.find('.//{http://collectionspace.org/services/authorization}account_permission')
    xmlTemplate.remove(perms)
    for child in xmlTemplate.getiterator():
        child.text = ''
        if child.tag == 'tenantId':
            child.text = tenantId

    #print etree.tostring(root)
    #print etree.tostring(xmlTemplate).replace('<', '\n<')
    #sys.exit()
