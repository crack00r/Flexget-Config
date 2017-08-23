
import feedparser, re, urllib2, requests
from bs4 import BeautifulSoup 

hoster = "uploaded"             # uploaded;uplaoded;oboom;cloudzer;filemonkey
outputFilename = "HDWorld.xml"   # wo soll die rss-datei gespeichert werden ?

## Schreibe RSS
outputFile = open(outputFilename, "w")
# Schreibe RSS
outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
outputFile.write("<rss version=\"2.0\">\n")
outputFile.write("<channel>\n")
outputFile.write("<title>HDWorldOrg RSS-Generator</title>\n")
outputFile.write("<description>Hd-world.org RSS Generator for Flexget</description>\n")
outputFile.write("<link>Hd-world.org</link>\n")
outputFile.write("<ttl> </ttl>\n")

def make_rss(title, lnk):
    outputFile.write("<item>\n")
    outputFile.write("<title>"+title+"</title>\n")
    outputFile.write("<link>"+lnk+"</link>\n")
    outputFile.write("</item>\n")

def replaceUmlauts(title):
    title = title.replace(unichr(228), "ae").replace(unichr(196), "Ae")
    title = title.replace(unichr(252), "ue").replace(unichr(220), "Ue")
    title = title.replace(unichr(246), "oe").replace(unichr(214), "Oe")
    title = title.replace(unichr(223), "ss")
    title = title.replace('&amp;', "&")
    title = "".join(i for i in title if ord(i)<128)
    return title

# def get_download(soup1, title):
    # rls_title = title
    # for title2 in soup1.findAll("h1", {"id" : re.compile('post.*')}):
        # hdw_url = title2.a["href"].replace("https","http")
        # req_page = requests.get(hdw_url).text
        # soup_ = BeautifulSoup(req_page)
        # links = soup_.findAll("div", {"class":"entry"})
        # print title2
        # for link in soup_.findAll('a', href=True, text='Uploaded'):
            # print link


for site in ('1','2','3','4','5','6','7','8','9'):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    url = ('http://hd-world.org/category/serien/page/' + site)
    response = opener.open(url)
    page = response.read()
    soup = BeautifulSoup(page, "lxml")
    for post in soup.findAll("div", {"class" : "post"}):
        for all in post.findAll("h1", {"id" : re.compile('post.*')}):
            for title in all.findAll('a'):
                title = title.getText()
                title = replaceUmlauts(title)
        for links in post.findAll('a', href=True):
            season = re.compile('.*S\d{2}E\d{2}.*')
            if season.match(title) and hoster.lower() in links.text.lower():
                print title
                lnk = links["href"]
                print lnk
                make_rss(title, lnk)

# Schreibe RSS footer
outputFile.write("</channel>\n")
outputFile.write("</rss>")
outputFile.close()
