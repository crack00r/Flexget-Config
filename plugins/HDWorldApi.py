# -*- coding: utf-8 -*-
import logging, re #, urllib, urllib2, json, HTMLParser, requests
from flexget.utils.tools import parse_filesize

from .BaseApi import BaseApi, SearchResultEntry

class HDWorldApi(BaseApi):
    """
        HD-World Api.
    """
    
    def reset(self):
        self.search_query_url = 'http://hd-world.org/index.php?'
        self.search_query_static = {"cat":0}
        self.search_query_param = "s"
        
        self.feed_query_url = "http://hd-world.org"
        self.feed_query_static = {"page":0,"category":""}
        self.feed_query_category = "category"
        self.feed_query_page = "page"
        self.feed_param_as_folder = ["category","page"]
        
    html_entry_class = "post"
    html_entry_title_element = "h2"
    html_entry_inner_class = "entry"
    
    html_feed_class = "post"
        
    def parse_results_page(self, results_page):
        archiv = results_page.find("div",id="archiv")
        
        result_entries = []
        for a in archiv.select("h1 > a"):
            # ignoring the fact that it could block the triple X movies with Vin Diesel, but I dont want pr0n in my library
            if 'XXX' in a.text:
                break
            
            result_entries.append({"title": a.text, "url": a['href']})
            
        ## check for more result pages        
        next_link = self.find_next_link(archiv)

        if len(result_entries) > 0 and next_link:
            next_page = self.get_url_content(next_link['href'])
            result_entries.extend(self.parse_results_page(next_page))
    
        return result_entries
    
    def find_next_link(self, page):
        nav = page.find("div", {"class":"navigation_x"})
        rightdiv = nav.find("div", {"class":"alignright"})
        
        next_link = None
        if rightdiv(text=re.compile(r'Seite')):
            next_links = rightdiv.find_all("a")
            last = None
            for last in next_links:pass
            next_link = last

        return next_link
        
    def parse_result_entry(self, entry_page):
    
        try:
            entry = entry_page.find("div", {"id":"content"})
            title = entry_page.find("div", {"class":self.html_entry_class}).find(self.html_entry_title_element).a.text
            
            entry = entry.find("div",{"class":self.html_entry_inner_class})

            size = 0
            sizetag = entry.find("strong", text=re.compile(r'Größe'))
            if sizetag:
                size = parse_filesize(sizetag.next_sibling.replace("|", "").strip())
            
            links = entry.findAll("a")
            dl_links = []
            imdb_url = self.find_imdb(str(entry))
            
            for link in links:
                if self.contains_hoster_variant(link.text):
                    dl_links.append(link["href"])

            return [SearchResultEntry(title, size, dl_links, imdb_url)]
        except Exception:
            #self.log_soup_to_file(entry_page)
            return []
        
        return [SearchResultEntry(title, size, dl_links, imdb_url)]
    def parse_feed_page(self, feed_page):
        feed_entries = []
        for post in feed_page.findAll("div", {"class" : self.html_feed_class}):
            for title in post.findAll("h1",limit=1):
                a = title.a
                url = a.get("href")
                
                feed_entries.extend( self.parse_result_entry( self.get_url_content(url)))
        return feed_entries