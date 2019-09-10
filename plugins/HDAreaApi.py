# -*- coding: utf-8 -*-
import logging, re #, urllib, urllib2, json, HTMLParser, requests
from flexget.utils.tools import parse_filesize

from .BaseApi import BaseApi, SearchResultEntry

class HDAreaApi(BaseApi):
    """
        HD-Area Api.
    """
    
    def reset(self):
        self.search_query_url = 'http://www.hd-area.org/?'
        self.search_query_static = {"s":"search"}
        self.search_query_param = "q"
        
        self.feed_query_url = self.search_query_url
        self.feed_query_static = {"pg":1,"s":""}
        self.feed_query_category = "s"
        self.feed_query_page = "pg"
        
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
                #log.verbose("#####" + url)
                #imdb_url = url[url.index('?')+1:].strip()
                imdb_url = url
                if imdb_url and not imdb_url.startswith('http'):
                    imdb_url =  'http://'+imdb_url
        
        links = entry_page.findAll("span", {"style":"display:inline;"})
        dl_links = []
        for link in links:
            if self.contains_hoster_variant(link.text):
                dl_links.append(link.a["href"])
        
        return [SearchResultEntry(title, size, dl_links, imdb_url)]
    def parse_feed_page(self, feed_page):
        feed_entries = []
        for all in feed_page.findAll("div", {"class" : "topbox"}):
            for title in all.findAll("div", {"class" : "title"},limit=1):
                a = title.a
                url = a.get("href")
                
                feed_entries.extend( self.parse_result_entry( self.get_url_content(url)))
        return feed_entries