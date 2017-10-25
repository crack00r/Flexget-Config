# -*- coding: utf-8 -*-
import logging, re, HTMLParser #, urllib, urllib2, json, requests

from flexget import plugin
from flexget.event import event
from flexget.utils.tools import parse_filesize
from flexget.utils.search import normalize_unicode
from .BaseSearchPlugin import BaseSearchPlugin, SearchResultEntry

log = logging.getLogger("SeriesSearchPlugin")
LANGUAGE = ['english', 'german']


DEFAULT_LANG = 'german'
DEFAULT_HOST = 'shareonline'

class SearchSerienjunkies(BaseSearchPlugin):

    schema = {
        'type': 'object',
        'properties': {
            'hoster': {'type': 'string'},
            'language': {'type': 'string', 'enum': LANGUAGE},
        },
        'additionalProperties': True
    }
    
    """
        Serienjunkies search plugin.
    """
    name = "searchSerienjunkies"
    query_url = 'http://serienjunkies.org/media/ajax/search/search.php'
    query_param_name = "string"
    static_link = "http://serienjunkies.org/?cat="
    
    EXCLUDES = {"Dauer:", "Download:", "Uploader:", "Größe:", "Tonhöhe:", "Sprache:", "Format:", "HQ-Cover:"}
    
    def init(self):
        self.log = logging.getLogger(self.name)
        self.config.setdefault('hoster', DEFAULT_HOST)
        self.config.setdefault('language', DEFAULT_LANG)
    
    def do_search(self, search_string):       
        return self.get_url_content(self.query_url, params={self.query_param_name:search_string}, method = "POST", json = True)
        
    def prepare_search_query(self, search_string):
        query = normalize_unicode(search_string)
        se = re.findall('((((|S)[\d]+(E|x)[\d]+)|(|S)[\d]+))$',query)[0][0]
        query = re.sub(se,'',query).strip()
        
        self.se = se
        self.query = query
        
        return query
        
    def parse_results_page(self, results):

        series_url = ''
        result_entries = []
        for r in results:
            ## unescape HTML-Entities eg: &auml; -> ä
            serienjunkies_name = HTMLParser.HTMLParser().unescape(r[1])
            
            ## workaround for SJ inconsistent naming
            ## - strip all non \w-chars, it strips numbers as well, but it should doesnt matter
            ## eg: You’re the Worst -> YouretheWorst, in serienjunkies search it is Youre the Worst -> YouretheWorst, so it will match.
            serienjunkies_name_stripped = re.sub('[^\w]+','',serienjunkies_name).lower()
            query_name_stripped = re.sub('[^\w]+', '', self.query).lower()

            if serienjunkies_name_stripped == query_name_stripped:
                series_url = self.static_link+str(r[0])
                result_entries.append({"title": r[1], "url": series_url})
                ## we only need one result.
                break

        return result_entries
    
    def parse_entry(self, target, filesize):
        for hoster in self.get_hoster_variants():
            r = target.find(text=re.compile(hoster))
            if r is not None:
                a = r.find_previous_sibling('a')
                return SearchResultEntry(title=target.strong.text, links=[a['href']], size=filesize)
    
    def parse_result_entry(self, entry_page):
    
        se = '\.' + self.se + '\.' ## if se = S01 or 01 dont match with Staffelpack Demo.S01E99.German.Dubstepped.DL.EbayHD.x264-VHS
        english = self.config['language'] == 'english'
    
        entries = []
        search_result_entries = []
        filesize = 0
        for p in entry_page.find_all('p'):
            if p.strong is not None and p.strong.text not in self.EXCLUDES:
                if english:
                    if p.strong.find(text=re.compile(se, flags=re.IGNORECASE)) and not p.strong.find(text=re.compile("german", flags=re.IGNORECASE)):
                        search_result_entries.append(self.parse_entry(p, filesize))
                else:
                    if p.strong.find(text=re.compile(se, flags=re.IGNORECASE)) and p.strong.find(text=re.compile("german", flags=re.IGNORECASE)):
                        search_result_entries.append(self.parse_entry(p, filesize))
            elif(p.find("strong", text="Größe:")):
                size = p.find("strong", text="Größe:").next_sibling
                
                ## experimental
                size = re.findall('([\d]+ [\w]+)',size.replace("|","").strip())[0]
                filesize = parse_filesize(size)
                
        ## check for more result pages
        next_link = entry_page.find("a", text="»")
        if next_link:
            next_page = self.get_url_content(next_link['href'])
            search_result_entries.extend(self.parse_result_entry(next_page))
        
        return [x for x in search_result_entries if x is not None]

@event('plugin.register')
def register_plugin():
    plugin.register(SearchSerienjunkies, 'searchSerienjunkies', groups=['search'], api_ver=2)
    
class SearchDokujunkies(SearchSerienjunkies):
    name = "searchDokujunkies"
    query_url = "http://dokujunkies.org/media/search.php"
    static_link = "http://dokujunkies.org/?p="
    
    def parse_results_page(self, results):

        series_url = ''
        result_entries = []
        for r in results:
            ## workaround for SJ inconsistent naming
            ## - strip all non \w-chars, it strips numbers as well, but it should doesnt matter
            ## eg: You’re the Worst -> YouretheWorst, in serienjunkies search it is Youre the Worst -> YouretheWorst, so it will match.
            serienjunkies_name = HTMLParser.HTMLParser().unescape(re.sub('[^\w]+','',r[1]))
            query_name = re.sub('[^\w]+', '', self.query)

            if query_name.lower() in serienjunkies_name.lower(): ## release information in search result, no strict string comparison possible, very lose implementation, could yield wrong results
                series_url = self.static_link+str(r[0])
                result_entries.append({"title": r[1], "url": series_url})
                ## we only need one result.
                break

        return result_entries
    
@event('plugin.register')
def register_plugin():
    plugin.register(SearchDokujunkies, 'searchDokujunkies', groups=['search'], api_ver=2)