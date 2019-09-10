# -*- coding: utf-8 -*-
import logging, re, json, collections
from datetime import datetime
from bs4 import BeautifulSoup
#from flexget import plugin
#from flexget.entry import Entry
from flexget.components.sites.utils import normalize_unicode
from flexget.utils import requests


#from flexget.event import event
#from flexget.config_schema import one_or_more
#from flexget.utils.tools import parse_filesize

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
    imdb_id = ""
    
    def __init__(self, title="", size=0, links=[], imdb_url=""):
        self.title = title
        self.size = size
        self.links = links
        self.imdb_url = imdb_url
        if imdb_url is not "":
            self.imdb_id = self.get_imdb_id_from_url(imdb_url)
        
    def getTitle(self):
        return self.title
    
    def getSize(self):
        return self.size
    
    def getLinks(self):
        return self.links
        
    def getImdbUrl(self):
        return self.imdb_url
    
    def getImdbId(self):
        return self.imdb_id
        
    def __str__(self):
     return self.title + " ("+str(self.size)+"GB, "+str(len(self.links))+" links, "+self.imdb_url+")"
     
    def get_imdb_id_from_url(self, url):
        res = re.findall('((tt|nm|co|ev|ch|ni)\d{7})', url)
        if len(res) > 0:
            return res[0][0]
        else:
            return ""


class BaseApi(object):
    config = {}
    search_query_url = ""
    search_query_static = {}
    search_query_param = ""
    search_param_as_folder = []
    
    feed_query_url = ""
    feed_query_static = {}
    feed_query_category = ""
    feed_query_page = ""
    feed_param_as_folder = []
    
    season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')


    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def init(self):
        #self.logger.info("init "+__name__)
        self.config.setdefault('hoster', [DEFAULT_HOST])
        hoster = self.config.get("hoster")
        if not isinstance(hoster, collections.Sequence):
            config["hoster"] = hoster.split(";")
            
        self.reset()
    
    def get_hoster_variants(self):
        hosters = self.config['hoster']
        
        hoster_variants = []
        for hoster in hosters:
            hoster_variants.extend( HOSTERVARIANTS[hoster] if hoster in HOSTERVARIANTS else [hoster] )
               
        return hoster_variants
    
    def get_url_content(self, url, params={}, method = "GET", json = False):
        self.logger.verbose("%s %s with %s",method,url,params)
        try:
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
        except Exception as err:
            self.logger.error("Error while web request: %s",err)
            return None
    
    def search(self, search_strings):
        self.init()
        
        entries = set()
        
        for search_string in search_strings:
            
            results_page = self.do_search(self.prepare_search_query(search_string))
            result_entries = self.parse_results_page(results_page)
            
            for result_entry in result_entries:
                entry_page = self.get_url_content(result_entry["url"])
                if not entry_page == None:
                    entries.update( self.parse_result_entry(entry_page) )
        
        return entries
        
    def do_search(self, search_string):
        #combine params
        params = self.search_query_static
        params.update({self.search_query_param:search_string})
        
        url = self.search_query_url
        for key in self.search_param_as_folder:
            url += "/"+key+"/"+str(params.pop(key))

        return self.get_url_content(url, params=params)
        
    def replace_sepcial_chars(self, string):
        string = string.replace(chr(228), "ae").replace(chr(196), "Ae")
        string = string.replace(chr(252), "ue").replace(chr(220), "Ue")
        string = string.replace(chr(246), "oe").replace(chr(214), "Oe")
        string = string.replace(chr(223), "ss")
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
    
    def feed(self, categories, count_pages, config):
        self.config = config
        self.init()
        
        entries = set()
        
        for category in categories:
            for p in range(count_pages):
                entries.update( self.do_feed(category, p+1) )
                
        return self.filter_entries(entries)
    
    def do_feed(self, category, page):
        params = self.feed_query_static
        
        feed_query_category = self.config.get("feed_query_category",self.feed_query_category)

        if feed_query_category != self.feed_query_category:
            if self.feed_query_category in params:
                params.pop(self.feed_query_category)
        
        params.update({feed_query_category:category})
        params.update({self.feed_query_page:str(page)})
        
        url = self.feed_query_url
        
        for key in self.feed_param_as_folder:
            url += "/"+key+"/"+params.pop(key)

        feed_page = self.get_url_content(url, params=params)
        if not feed_page == None:
            return self.parse_feed_page(feed_page)
        else:
            return []
        
    def filter_entries(self, entries):
        if self.config.get("only_movies",False):
            return list( filter(self.is_movie, entries) )
        if self.config.get("only_series",False):
            return list( filter(self.is_series, entries) )
        
        return entries
        
    def is_series(self, entry):
        if self.season.match(entry.getTitle()):
            return True
        else:
            return False
            
    def is_movie(self, entry):
        return not self.is_series(entry)
        
    def generate_rss(self, entries, file):
        
        outputFile = open(file, "w")
        outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
        outputFile.write("<rss version=\"2.0\">\n")
        outputFile.write("\t<channel>\n")
        outputFile.write("\t\t<title>"+ type(self).__name__ +" RSS-Generator</title>\n")
        outputFile.write("\t\t<description>"+ type(self).__name__ +" RSS Generator for Flexget</description>\n")
        outputFile.write("\t\t<link>"+self.feed_query_url+"</link>\n")
        outputFile.write("\t\t<lastBuildDate>"+datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')+"</lastBuildDate>\n")
        outputFile.write("\t\t<ttl> </ttl>\n")
        
        for entry in entries:
            for link in entry.getLinks():
                outputFile.write("\t\t<item>\n")
                outputFile.write("\t\t\t<title>"+normalize_unicode(entry.getTitle())+"</title>\n")
                outputFile.write("\t\t\t<link>"+link+"</link>\n")
                
                if entry.getImdbId():
                    outputFile.write("\t\t\t<imdb_id>"+entry.getImdbId()+"</link>\n")
                
                if entry.getSize():
                    outputFile.write("\t\t\t<size>"+ ( "{0:.2f}".format(entry.getSize()) ) +"</size>\n")
                outputFile.write("\t\t</item>\n")
        
        outputFile.write("\t</channel>\n")
        outputFile.write("</rss>")
        outputFile.close()
        
    def find_imdb(self, text):
        urls = re.findall('((http:\/\/|www\.|https:\/\/www\.|)imdb.com\/title\/tt\d+(\/|))', str(text))
        if len(urls)>0:
            return urls[0][0]
        else:
            return ""
    