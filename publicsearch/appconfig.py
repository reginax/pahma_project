# global variables

from os import path
from common import cspace # we use the config file reading function

config = cspace.getConfig(path.dirname(__file__), 'search')

MAXMARKERS = config.get('search', 'MAXMARKERS')
MAXRESULTS = config.get('search', 'MAXRESULTS')
MAXLONGRESULTS = config.get('search', 'MAXLONGRESULTS')
MAXFACETS = config.get('search', 'MAXFACETS')
IMAGESERVER = config.get('search', 'IMAGESERVER')
BMAPPERSERVER = config.get('search', 'BMAPPERSERVER')
BMAPPERDIR = config.get('search', 'BMAPPERDIR')
BMAPPERCONFIGFILE = config.get('search', 'BMAPPERCONFIGFILE')
SOLRSERVER = config.get('search', 'SOLRSERVER')
SOLRCORE = config.get('search', 'SOLRCORE')
LOCALDIR = config.get('search', 'LOCALDIR')
DROPDOWNS = config.get('search', 'DROPDOWNS').split(',')
SEARCH_QUALIFIERS = config.get('search', 'SEARCH_QUALIFIERS').split(',')

# still need to move this into a config file.
# could be the same one as above, or a different one.
PARMS = {
    # this first one is special
    'keyword': ['Keyword', 'true', 'a keyword search value, please', 'text', ''],

    # the rest are mapping the solr field names to django form labels and fields
    'csid': ['id', 'true', '', 'id', ''],
    'accession': ['Object Number', 'true', '', 'objectnumber_s', ''],
    'objectname': ['Object Name', 'true', '', 'objectname_txt', ''],
    'collector': ['Collector', 'true', '', 'collector_txt', ''],
    'collectiondate': ['Collection Date', 'true', '', 'collectiondate_txt', ''],
    'location': ['Location', 'true', '', 'location_txt', ''],
    'county': ['County', 'true', '', 'collcounty_txt', ''],
    'state': ['State', 'true', '', 'collstate_s', ''],
    'country': ['Country', 'true', '', 'collcountry_s', ''],
    'medium': ['Medium', 'true', '', 'medium_txt', ''],
    'culture': ['Culture', 'true', '', 'culture_txt', ''],
    'provenance': ['Provenance', 'true', '', 'provenance_txt', ''],
    'description': ['Description', 'true', '', 'description_txt', ''],
    'L1': ['L1', 'true', '', 'location_0_coordinate', ''],
    'L2': ['L2', 'true', '', 'location_1_coordinate', ''],
    'blobs': ['blob_ss', 'true', '', 'blob_ss', ''],
}
