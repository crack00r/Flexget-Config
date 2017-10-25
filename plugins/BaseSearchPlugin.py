#from __future__ import unicode_literals, division, absolute_import
import logging, json, datetime, time #, urllib, urllib2, re, , HTMLParser, requests

from bs4 import BeautifulSoup
from flexget import plugin
from flexget.entry import Entry
from flexget.utils.search import normalize_unicode
from flexget.utils import requests

#from flexget.event import event
#from flexget.config_schema import one_or_more
#from flexget.utils.tools import parse_filesize

log = logging.getLogger("BaseSearchPlugin")
ENUM_HOSTER = ['uploaded', 'shareonline']
DEFAULT_HOST = 'shareonline'

HOSTERVARIANTS = {
    'shareonline': ['shareonline','share online','share-online','share-online.biz'],
    'uploaded': ['uploaded','uploaded.to','uploaded.net'],
    'rapidgator': ['rapidgator', 'rapidgator.net'],
    'filer': ['filer', 'filer.net'],
    'oboom': ['oboom', 'oboom.com'],
    'zippyshare': ['zippyshare', 'zippyshare.com']
}

class SearchResultEntry(object):

    links = []
    title = ""
    size = 0
    imdb_url = ""
    
    def __init__(self, title="", size=0, links=[], imdb_url=""):
        self.title = title
        self.size = size
        self.links = links
        
    def getTitle(self):
        return self.title
    
    def getSize(self):
        return self.size
    
    def getLinks(self):
        return self.links
        
    def getImdbUrl(self):
        return self.imdb_url   


class BaseSearchPlugin(object):
    config = {}
    name = "BaseSearchPlugin"
    query_url = ""
    query_static = {}
    query_param_name = ""
       
    schema = {
        'type': 'object',
        'properties': {
            'hoster': {'type': 'string'}
        },
        'additionalProperties': False
    }
    
    def log_soup_to_file(self, soup):
        filename = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "-result-page.html"
        log.info("Saved output to "+filename)
        with open(filename, "w") as file:
            file.write(str(soup))
    
    def init(self):
        self.log = logging.getLogger(self.name)
        self.config.setdefault('hoster', DEFAULT_HOST)
    
    def get_hoster_variants(self):
        hosters = self.config['hoster'].split(";")
        
        hoster_variants = []
        for hoster in hosters:
            hoster_variants.extend( HOSTERVARIANTS[hoster] if hoster in HOSTERVARIANTS else [hoster] )
               
        return hoster_variants
    
    def get_url_content(self, url, params={}, method = "GET", json = False):
        if method is "GET":
            result = requests.get(url, params=params)
        elif method is "POST":
            result = requests.post(url, data=params)
        
        if json:
            if result.content:
                return result.json()
            else:
                return {}
        else:
            return BeautifulSoup(result.content, "html5lib")
    
    @plugin.internet(log)
    def search(self, task, entry, config):
        
        self.config = config
        self.init()

        entries = set()
        
        for search_string in entry.get('search_strings', [entry['title']]):
            
            results_page = self.do_search(self.prepare_search_query(search_string))
            result_entries = self.parse_results_page(results_page)
            
            for result_entry in result_entries:
                entry_page = self.get_url_content(result_entry["url"])
                search_result_entries = self.parse_result_entry(entry_page)
                entries.update(self.get_entries(search_result_entries))
        return entries
        
    def do_search(self, search_string):
        #combine params
        params = self.query_static
        params.update({self.query_param_name:search_string})
        
        return self.get_url_content(self.query_url, params=params)
        
    def replace_sepcial_chars(self, string):
        string = string.replace(unichr(228), "ae").replace(unichr(196), "Ae")
        string = string.replace(unichr(252), "ue").replace(unichr(220), "Ue")
        string = string.replace(unichr(246), "oe").replace(unichr(214), "Oe")
        string = string.replace(unichr(223), "ss")
        string = string.replace('&amp;', "&")
        string = string.replace("(","").replace(")","")
        string = string.replace(":","")
        string = "".join(i for i in string if ord(i)<128)
        
        return string 
    
    def prepare_search_query(self, search_string):
        return self.replace_sepcial_chars(normalize_unicode(search_string))
        
    def contains_hoster_variant(self, text):
        if not text.strip():
            return False
        
        hoster_variants = self.get_hoster_variants()
        
        for hoster_variant in hoster_variants:
            if hoster_variant.lower() in text.strip().lower():
                return True
        return False
        
    def get_entries(self, search_result_entries):
    
        entries = set()
        for search_result_entry in search_result_entries:
            for link in search_result_entry.getLinks():
                entry = Entry()
                entry['title'] = search_result_entry.getTitle()
                entry['url'] = link
                #entry['imdb_url'] = search_result_entry.getImdbUrl() ##experimental
                
                if search_result_entry.getSize() > 0:
                    entry['content_size'] = search_result_entry.getSize()
                    
                log.verbose("Entry -> Title:"+ search_result_entry.getTitle()+", Link: " + link + ", Size: "+ str(search_result_entry.getSize()))
                entries.add(entry)

        return entries