#!/usr/bin/env python
# -- coding: utf-8 --
import feedparser, re, requests, datetime
from BeautifulSoup import BeautifulSoup

### Anpassen
hoster = "ul"               # ul, so oder alle
outputFilename = "rss.xml"  # wo soll die rss-datei gespeichert werden ?
ThreeDays = "True"

def formatDate(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

def range_checkr(link, title, language):
    pattern = re.match(".*S\d{2}E\d{2}-\w?\d{2}.*", title)
    if pattern is not None:
        range0 = re.sub(r".*S\d{2}E(\d{2}-\w?\d{2}).*",r"\1", title).replace("E","")
        number1 = re.sub(r"(\d{2})-\d{2}",r"\1", range0)
        number2 = re.sub(r"\d{2}-(\d{2})",r"\1", range0)
        title_cut = re.findall(r"(.*S\d{2}E)(\d{2}-\w?\d{2})(.*)",title)
        for count in range(int(number1),(int(number2)+1)):
            NR = re.match("d\{2}", str(count))
            if NR is not None:
                title1 = title_cut[0][0] + str(count) + ".*" + title_cut[0][-1]
                range_parse(link, title1, language)
            else:
                title1 = title_cut[0][0] + "0" + str(count) + ".*" + title_cut[0][-1]
                range_parse(link, title1, language)
    else:
        parse_download(link, title, language) 

def range_parse(series_url, search_title, language):
    req_page = requests.get(series_url).text
    soup = BeautifulSoup(req_page)
    titles = soup.findAll(text=re.compile(search_title))
    parse_download(series_url, title, language)

def parse_download(series_url, search_title, language):
    req_page = requests.get(series_url).text
    soup = BeautifulSoup(req_page)
    title = soup.find(text=re.compile(search_title))
    if title:
        links = title.parent.parent.findAll('a')
        for link in links:
            url = link['href']
            pattern = '.*%s_.*' % hoster
            if re.match(pattern, url):
                print title
                print url
                make_rss(title, url, language)

def make_rss(title, link, language):
    outputFile.write("\t<item>\n")
    outputFile.write("\t\t<title>"+language+" "+title+"</title>\n")
    outputFile.write("\t\t<link>"+link+"</link>\n")
    outputFile.write("\t</item>\n")

## Schreibe RSS
outputFile = open(outputFilename, "w")
# Schreibe RSS
outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
outputFile.write("<rss version=\"2.0\">\n")
outputFile.write("<channel>\n")
outputFile.write("<title>SerienJunkies-RSS Generator</title>\n")
outputFile.write("<description>Serienjunkies.org RSS Generator for Flexget</description>\n")
outputFile.write("<link>Serienjunkies.org</link>\n")
outputFile.write("<ttl> </ttl>\n")

feed = feedparser.parse('http://serienjunkies.org/xml/feeds/episoden.xml')
if hoster == "alle":
    hoster = "."
today_ = datetime.datetime.now()
yesterday_ = datetime.datetime.now() - datetime.timedelta(days = 1)
daybeforeyesterday_ = datetime.datetime.now() - datetime.timedelta(days = 2)
for post in feed.entries:
    feed_date = re.sub(r"(\w{3},\s\d{2}\s\w{3}\s\d{4}).*", r"\1", post.published)
    today = re.sub(r"(\w{3},\s\d{2}\s\w{3}\s\d{4}).*", r"\1", formatDate(today_))
    yesterday = re.sub(r"(\w{3},\s\d{2}\s\w{3}\s\d{4}).*", r"\1", formatDate(yesterday_))
    daybeforeyesterday = re.sub(r"(\w{3},\s\d{2}\s\w{3}\s\d{4}).*", r"\1", formatDate(daybeforeyesterday_))
    if not ThreeDays:
        if feed_date == today:
            link = post.link
            language = re.sub(r'\[(.*)\].*', r'\1', post.title)
            title = re.sub('\[.*\] ', '', post.title)
            range_checkr(link,title,language)
    else:
        if (feed_date == today) or (feed_date == yesterday) or (feed_date == daybeforeyesterday):
            link = post.link
            language = re.sub(r'\[(.*)\].*', r'\1', post.title)
            title = re.sub('\[.*\] ', '', post.title)
            range_checkr(link,title,language)

# Schreibe RSS footer
outputFile.write("</channel>\n")
outputFile.write("</rss>")
outputFile.close()
