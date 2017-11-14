# -*- coding: utf-8 -*-
import logging, re #, urllib, urllib2, json, HTMLParser, requests

from flexget import plugin
from flexget.event import event
from flexget.utils.tools import parse_filesize
from .BaseSearchPlugin import BaseSearchPlugin, SearchResultEntry

#CATEGORIES = {
#    # Hoster
#    'Uploaded': "ul",
#    'ShareOnline': "so",
#
#    # Sprache
#    'Sprache': "deutsch",
#
#    # Movies
#    'BluRay 720p': 2,
#    'BluRay 1080p': 5,
#    'XviD': 15,
#    'BRRip': 16,
#
#    # TV
#    'HDTV': 7,
#    'SDTV': 24,
#    'TV WEB-DL': 14
#}

#HOSTERVARIANTS = {
#    'shareonline': ['shareonline','share online','share-online','share-online.biz'],
#    'uploaded': ['uploaded','uploaded.to','uploaded.net']
#}

log = logging.getLogger("MovieSearchPlugin")
#HOSTER = ['uploaded', 'shareonline']
#DEFAULT_HOST = 'shareonline'     

class SearchHdarea(BaseSearchPlugin):
    """
        HD-Area search plugin.
    """
    name = "searchHDArea"
    query_url = 'http://www.hd-area.org/?'
    query_static = {"s":"search"}
    query_param_name = "q"
    
    #def do_search(self, search_string):
        
        #return self.get_url_content('http://www.hd-area.org/?', {'s':'search','q':search_string})
    #    return self.get_url_content(self.query_url, self.query_static.update({self.query_param_name:search_string}))
        
    def parse_results_page(self, results_page):
        results_page = results_page.find("div",id="content").find("div", {"class":"whitecontent"})

        result_entries = []
        for a in results_page.findAll("a", recursive=False):

            # ignoring the fact that it could block the triple X movies with Vin Diesel, but I dont want pr0n in my library
            if 'XXX' in a.text:
                break
            
            result_entries.append({"title": a.text, "url": a['href']})
            
        ## check for more result pages
        next_link = results_page.find("a", text=" Vorwärts »")
        if len(result_entries) > 0 and next_link:
            next_page = self.get_url_content(next_link['href'])
            result_entries.extend(self.parse_results_page(next_page))
    
        return result_entries
        
    def parse_result_entry(self, entry_page):
    
        title = entry_page.find("div", id="title").find("a")["title"]
        
        beschreibung = entry_page.find("div", {"class":"beschreibung"})
        size = 0
        
        sizetag = beschreibung.find("strong", text="Größe:")
        if sizetag:
            size = parse_filesize(sizetag.next_sibling)
        #else: 
        #    print "no sizetag!!"
        #    pre = beschreibung.find("pre").text
        #    if pre:
        #        se = re.find('(File size)[\s]+:([ \d\.\w]+)',pre)
        
        imdb_url = ""
        
        links = entry_page.find("div", id="content").findAll("a")
        for link in links:
            if "imdb" in link.text.lower():
                url = link['href']
                imdb_url = url[url.index('?')+1:].strip()
                if imdb_url and not imdb_url.startswith('http'):
                    imdb_url =  'http://'+imdb_url
        
        links = entry_page.findAll("span", {"style":"display:inline;"})
        dl_links = []
        for link in links:
            if self.contains_hoster_variant(link.text):
                dl_links.append(link.a["href"])
        
        return [SearchResultEntry(title, size, dl_links, imdb_url)]

@event('plugin.register')
def register_plugin():
    plugin.register(SearchHdarea, 'searchHdarea', interfaces=['search'], api_ver=2)
    
    
    
class SearchHdworld(BaseSearchPlugin):
    """
        HD-World search plugin.
    """
    name = "searchHDWorld"
    query_url = 'http://hd-world.org/index.php?'
    query_static = {"cat":0}
    query_param_name = "s"
    
    html_entry_class = "post"
    html_entry_title_element = "h2"
        
    def parse_results_page(self, results_page):
        archiv = results_page.find("div",id="archiv")
        
        result_entries = []
        for a in archiv.select("h1 > a"):
            # ignoring the fact that it could block the triple X movies with Vin Diesel, but I dont want pr0n in my library
            if 'XXX' in a.text:
                break
            
            result_entries.append({"title": a.text, "url": a['href']})
            
        ## check for more result pages
        next_link = archiv.find("a", {"class":"nextpostslink", "text":"»"})
        if len(result_entries) > 0 and next_link:
            next_page = self.get_url_content(next_link['href'])
            result_entries.extend(self.parse_results_page(next_page))
    
        return result_entries
        
    def parse_result_entry(self, entry_page):
    
        try:
            beitrag = entry_page.find("div", {"id":"content"})
            title = entry_page.find("div", {"class":self.html_entry_class}).find(self.html_entry_title_element).a.text
        
            size = 0
            sizetag = beitrag.find("strong", text="Größe: ")
            if sizetag:
                size = parse_filesize(sizetag.next_sibling.replace("|", "").strip())
                   
            links = entry_page.findAll("a")
            dl_links = []
            imdb_url = ""
            for link in links:
                if "imdb" in link.text.lower():
                    imdb_url = link["href"]
                if self.contains_hoster_variant(link.text):
                    dl_links.append(link["href"])
        
            return [SearchResultEntry(title, size, dl_links, imdb_url)]
        except Exception:
            log.error("Got unexpected result page - maybe no valid search results on that page?")
            #self.log_soup_to_file(entry_page)
        finally:
            return []
        
@event('plugin.register')
def register_plugin():
    plugin.register(SearchHdworld, 'searchHdworld', interfaces=['search'], api_ver=2)
    
class SearchMovieBlog(SearchHdworld):
    """
        MovieBlog search plugin.
        
        
        Bug:
        
        This Plugins raises a known Flexget issue:
        
        ## https://github.com/Flexget/Flexget/issues/847
        ## Solution:
        ## In flexget\plugins\input\discover.py's entry_complete method, insert:
        if entry not in search_results:
            # Rebuild search_results in place to recompute all its hashes
            search_results_copy = list(search_results)
            search_results.intersection_update([])      # empty search_results set in place
            search_results.update(search_results_copy)  # repopulate search_results set in place
            
        ##before the line:

        search_results.remove(entry)  
    """
    name = "searchMovieBlog"
    query_url = 'http://www.movie-blog.org/index.php?'
    
    html_entry_class = "beitrag"
    html_entry_title_element = "h1"
    
@event('plugin.register')
def register_plugin():
    plugin.register(SearchMovieBlog, 'searchMovieBlog', interfaces=['search'], api_ver=2)