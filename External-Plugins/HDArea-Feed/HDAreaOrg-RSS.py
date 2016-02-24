import feedparser, re, urllib2, requests
from BeautifulSoup import BeautifulSoup 

quality = "720p"
hoster = "uploaded"             # uploaded;uplaoded;oboom;cloudzer;filemonkey
imdb_title = "True"             # Imdb oder Hdarea Titel in die xml schreiben (true = imdb-titel)
outputFilename = "HDArea.xml"   # wo soll die rss-datei gespeichert werden ?

## Schreibe RSS
outputFile = open(outputFilename, "w")
# Schreibe RSS
outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
outputFile.write("<rss version=\"2.0\">\n")
outputFile.write("<channel>\n")
outputFile.write("<title>HDAreaOrg RSS-Generator</title>\n")
outputFile.write("<description>Hd-area.org RSS Generator for Flexget</description>\n")
outputFile.write("<link>Hd-area.org</link>\n")
outputFile.write("<ttl> </ttl>\n")

def make_rss(title, link):
    outputFile.write("<item>\n")
    outputFile.write("<title>"+title+"</title>\n")
    outputFile.write("<link>"+link+"</link>\n")
    outputFile.write("</item>\n")

def replaceUmlauts(title):
    title = title.replace(unichr(228), "ae").replace(unichr(196), "Ae")
    title = title.replace(unichr(252), "ue").replace(unichr(220), "Ue")
    title = title.replace(unichr(246), "oe").replace(unichr(214), "Oe")
    title = title.replace(unichr(223), "ss")
    title = title.replace('&amp;', "&")
    title = "".join(i for i in title if ord(i)<128)
    return title

def get_download(soup1, title):
    rls_title = title
    for title in soup1.findAll("div", {"class" : "title"}):
        hda_url = title.a["href"].replace("https","http")
        req_page = requests.get(hda_url).text
        soup_ = BeautifulSoup(req_page)
        links = soup_.findAll("span", {"style":"display:inline;"})
        for link in links:
            url = link.a["href"]
            if imdb_title:
                if hoster.lower() in link.text.lower():
                    get_year(soup1, url, rls_title)
            else:
                make_rss(rls_title,url)
                print url+"\n"

def get_year(soup1, dlLink, rls_title):
    imdb_url = soup1.find("div", {"class" : "boxrechts"})
    imdb_url = unicode.join(u'',map(unicode,imdb_url))
    imdb_url = re.sub(r'.*(imdb.*)"\starget.*', r'http://\1', imdb_url)
    if "http" in imdb_url:
        imdb_url = re.findall(r'(https?:\/\/?imdb.com.+)', imdb_url)[0]
        page = urllib2.urlopen(imdb_url).read()
        imdb_site = BeautifulSoup(page)
        year_pattern = re.compile(r'[0-9]{4}')
        year = imdb_site.find("span", {"class" : "nobr"})
        year = unicode.join(u'',map(unicode,year))
        year = re.sub(r".*([0-9]{4}).*", r"\1", year)
        orig_title = imdb_site.find("span", {"class" : "itemprop"}).getText()
        title = replaceUmlauts(orig_title)
        print title+" ("+year+")"
        print dlLink+"\n"
        make_rss(title,dlLink)
    
for site in ('top-rls','movies','Old_Stuff','Cinedubs'): #
    address = ('http://hd-area.org/index.php?s=' + site)
    page = urllib2.urlopen(address).read()
    soup = BeautifulSoup(page)
    for all in soup.findAll("div", {"class" : "topbox"}):
        for title in all.findAll("div", {"class" : "title"}):
            title = title.getText()
            title = replaceUmlauts(title)
            season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')
            if (quality in title) and not season.match(title):
                get_download(all, title)

# Schreibe RSS footer
outputFile.write("</channel>\n")
outputFile.write("</rss>")
outputFile.close()
