#!/usr/bin/env python3
import feedparser, re, urllib, urllib2, requests, threading
from urllib import urlopen
from bs4 import BeautifulSoup
from flexget.components.sites.utils import normalize_unicode


# Einstellungen:
quality = ["720p", "1080p", "2160p", "4k"]
sites = ["Serien"]
hoster = ["share online", "share-online", "share-online.biz", "uploaded","filer", "rapidgator"]
rssname = "HDArea.xml"

# Skript startet hier:
threads = []

rss = open(rssname, "w")
rss.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
rss.write("<rss version=\"2.0\">\n")
rss.write("<channel>\n")
rss.write("<title>HDAreaOrg RSS-Generator</title>\n")
rss.write("<description>Hd-area.org RSS Generator for Flexget</description>\n")
rss.write("<link>Hd-area.org</link>\n")
rss.write("<ttl> </ttl>\n")

def make_rss(guid, title, link):
    rss.write("<item>\n")
    rss.write("<guid>"+guid+"</guid>\n")
    rss.write("<title>"+title+"</title>\n")
    rss.write("<link>"+link+"</link>\n")
    rss.write("</item>\n")

def replace_umlauts(title):
    title = title.replace(chr(228), "ae").replace(chr(196), "Ae")
    title = title.replace(chr(252), "ue").replace(chr(220), "Ue")
    title = title.replace(chr(246), "oe").replace(chr(214), "Oe")
    title = title.replace(chr(223), "ss")
    title = title.replace('&amp;', "&")
    title = "".join(i for i in title if ord(i)<128)
    return title

def fetch_imdb_title(url):
    if not url:
        return ''
    page = urlopen(url).read()
    soup = BeautifulSoup(page, "lxml")
    return soup.title.text.replace(" - IMDb", "")

def fetch_releases(site):
    url = ("https://hd-area.org/index.php?c=" + site)
    page = urlopen(url).read()
    soup = BeautifulSoup(page, "lxml")

    season_re = re.compile(r".*S\d|\Sd{2}|eason\d|eason\d{2}.*")
    quality_re = re.compile(str.join("|", quality))

    for release in soup.find_all("div", {"class" : "topbox"}):
        imdb_url = ""
        imdb = re.search(r"(https?://(?:www\.)?imdb\.com/title/tt\d+/?)", str(release), re.I)
        if imdb:
            imdb_url = imdb.group(0)

        title = release.select_one("div.boxlinks > #title > a")["title"]

        if re.search(quality_re, title) and not season_re.match(title):

            links = release.find_next("div", {"class" : "download"})
            links = links.select("div.beschreibung > span[style='display:inline;'] > a")
            for link in links:
                url = link["href"]
                if link.text.lower() in hoster:
                    imdb_title = fetch_imdb_title(imdb_url)
                    imdb_title = replace_umlauts(title)
                    if not imdb_title:
                        imdb_title = title
                    print("title:   " + imdb_title)
                    print("release: " + title)
                    print("imdb:    " + imdb_url)
                    print("url:     " + url + "\n")
                    make_rss(title, imdb_title, url)

class HDAreaThread(threading.Thread):
    def __init__(self, site):
        threading.Thread.__init__(self)
        self.site = site
    def run(self):
        fetch_releases(self.site)

for site in sites:
    thread = HDAreaThread(site)
    thread.start()
    threads.append(thread)

for t in threads:
    t.join()

rss.write("</channel>\n")
rss.write("</rss>")
rss.close()
