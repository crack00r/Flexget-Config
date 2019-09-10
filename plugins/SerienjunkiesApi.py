# -*- coding: utf-8 -*-
import logging, re, html.parser, feedparser, codecs
from datetime import datetime
from flexget.utils.tools import parse_filesize
from flexget.components.sites.utils import normalize_unicode

from .BaseApi import BaseApi, SearchResultEntry



class SerienjunkiesApi(BaseApi):
    """
        Serienjunkies Api.
    """
    
    def reset(self):
        self.search_query_url = 'http://serienjunkies.org/media/ajax/search/search.php'
        self.search_query_param = "string"
        self.search_static_link = "http://serienjunkies.org/?cat="
    
        self.feed_query_url = "http://serienjunkies.org/xml/feeds/"    
    
    EXCLUDES = {"Dauer:", "Download:", "Uploader:", "Größe:", "Tonhöhe:", "Sprache:", "Format:", "HQ-Cover:"}
        
    def do_search(self, search_string):       
        return self.get_url_content(self.search_query_url, params={self.search_query_param:search_string}, method = "POST", json = True)
        
    def prepare_search_query(self, search_string):
        query = normalize_unicode(search_string)
        
        se = re.findall('((((|S|s)[\d]+(e|E|x)[\d]+)|(|S|s)[\d]+))$',query)[0][0]
        query = re.sub(se,'',query).strip()
        
        self.se = se
        self.query = query
        
        self.logger.verbose("search: '%s', SXXEXX: '%s'", query, se)
        
        return query
        
    def parse_results_page(self, results):
        
        series_url = ''
        result_entries = []
        for r in results:
            ## unescape HTML-Entities eg: &auml; -> ä
            serienjunkies_name = html.parser.HTMLParser().unescape(r[1])
            
            ## workaround for SJ inconsistent naming
            ## - strip all non \w-chars, it strips numbers as well, but it should doesnt matter
            ## eg: You’re the Worst -> YouretheWorst, in serienjunkies search it is Youre the Worst -> YouretheWorst, so it will match.
            serienjunkies_name_stripped = re.sub('[^\w]+','',serienjunkies_name).lower()
            query_name_stripped = re.sub('[^\w]+', '', self.query).lower()

            if serienjunkies_name_stripped == query_name_stripped:
                series_url = self.search_static_link+str(r[0])
                result_entries.append({"title": r[1], "url": series_url})
                ## we only need one result.
                break

        return result_entries
    
    def parse_entry(self, target, filesize):
        links = []
        found_hoster = False
        for hoster in self.get_hoster_variants():
            r = target.find(text=re.compile(hoster))
            if r is not None:
                found_hoster = True
                
                a = r.find_previous_sibling('a')
                
                if a is not None:
                    links.append(a['href'])
                    continue

                link = re.findall('<a\s(?:[^\s>]*?\s)*?href="(?:mailto:)?(.*?)".*?>(.+?)<\/a> \| '+hoster, str(target))
                if len(link)>0:
                    links.append(link[0][0])
                    continue
   
        links = list(dict.fromkeys(links))

        if len(links) > 0:
            self.logger.verbose("found %i suitable links for %s",len(links),target.strong.text)
            return SearchResultEntry(title=target.strong.text, links=links, size=filesize)
        else:
            if found_hoster:
                self.logger.warning("found a suitable-hoster for %s, but it has no links?!",target.strong.text)
                
            self.logger.verbose("no suitable link found for %s",target.strong.text)
            return None
    
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
                size = re.sub(' +',' ',size) # remove multiple whitespaces
                size = size.replace("|","").strip() # remove | and strip whitespaces
                size = re.findall('([\d]+ [\w]+)',size)
                if len(size) > 0:
                    filesize = parse_filesize(size[0])
                
        ## check for more result pages
        next_link = entry_page.find("a", text="»")
        if next_link:
            next_page = self.get_url_content(next_link['href'])
            search_result_entries.extend(self.parse_result_entry(next_page))
        
        return [x for x in search_result_entries if x is not None]

    def feed(self, category):
        self.init()
        url = self.feed_query_url + category + ".xml"
        feed=feedparser.parse(url)
        
        self.logger.info("loaded %s with %i entries", url, len(feed.entries))
        
        return feed.entries
    
    def generate_rss(self, entries, config={}):
        prefix = config.get("filename","rss_feed_")
        file_count = config.get("file_count",10)
        entry_count = config.get("entry_count",200)
        
        entry_index=0
        file_index=1
        while file_index<(file_count+1):
            #create file and begin of RSS-Feed
            outputFile = open(prefix+str(file_index)+".xml", "w")
            outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
            outputFile.write("<rss version=\"2.0\">\n")
            outputFile.write("\t<channel>\n")
            outputFile.write("\t\t<title>SerienJunkies-RSS Generator</title>\n")
            outputFile.write("\t\t<description>Serienjunkies.org RSS Generator for Flexget</description>\n")
            outputFile.write("\t\t<link>Serienjunkies.org</link>\n")
            outputFile.write("\t\t<language>de</language>\n")
            outputFile.write("\t\t<lastBuildDate>"+datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')+"</lastBuildDate>\n")
            outputFile.write("\t\t<copyright>serienjunkies.org</copyright>\n")

            #create every item
            while entry_index<(entry_count*file_index):
                if entry_index==len(entries): 
                    break
                outputFile.write("\t\t<item>\n")
                outputFile.write("\t\t\t<title>"+normalize_unicode(entries[entry_index].title)+"</title>\n")
                outputFile.write("\t\t\t<link>"+ entries[entry_index].link +"#"+entries[entry_index].title+"-"+datetime.now().strftime('%Y%m%d%H%M%S')+"</link>\n")
                outputFile.write("\t\t</item>\n")
                entry_index +=1
                #create end of RSS
            outputFile.write("\t</channel>\n")
            outputFile.write("</rss>")
            outputFile.close()
            file_index +=1
        