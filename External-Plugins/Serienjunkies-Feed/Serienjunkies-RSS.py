import sys, feedparser, codecs, re
from datetime import datetime
from flexget.components.sites.utils import normalize_unicode

### setup , please:
# output_folder for rss_feed_1-10.xml with "/" on the end
OutputFolder= "./"
#max. 200 entries per file
#if items from RSS is less than given files, the last files will be empty
files = 10


#create variables
i=0
j=1
feed=feedparser.parse('http://serienjunkies.org/xml/feeds/episoden.xml')
print "items in RSS-Feed = "+str(len(feed.entries))
#schreibe RSS
while j<(files+1):
  #create file and begin of RSS-Feed
  print "Create outputfile: rss_feed_"+str(j)+".xml"
  outputFile = codecs.open(OutputFolder+"rss_feed_"+str(j)+".xml", "w", "utf-8")
  outputFile.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
  outputFile.write("<rss version=\"2.0\">\n")
  outputFile.write("\t<channel>\n")
  outputFile.write("\t\t<title>SerienJunkies-RSS Generator</title>\n")
  outputFile.write("\t\t<description>Serienjunkies.org RSS Generator for Flexget</description>\n")
  outputFile.write("\t\t<link>Serienjunkies.org</link>\n")
  outputFile.write("\t\t<language>de</language>\n")
  outputFile.write("\t\t<lastBuildDate>"+datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0200')+"</lastBuildDate>\n")
  outputFile.write("\t\t<copyright>serienjunkies.org</copyright>\n")

  #create every item
  while i<(200*j):
    if i==len(feed.entries): break
    outputFile.write("\t\t<item>\n")
    outputFile.write("\t\t\t<title>"+feed.entries[i].title+"</title>\n")
    outputFile.write("\t\t\t<link>"+ feed.entries[i].link +"#"+feed.entries[i].title+"-"+datetime.now().strftime('%Y%m%d%H%M%S')+"</link>\n")
    outputFile.write("\t\t</item>\n")
    i +=1
  #create end of RSS
  outputFile.write("\t</channel>\n")
  outputFile.write("</rss>")
  outputFile.close()
  j +=1

