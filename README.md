# Flexget-Config

Flexget-Config by snickers<br>
thanks to [topy](https://github.com/topy) for Plugins <br>

Mainly for German Users, but help with other languages is appreciated <br>
<br>
- Easy to use Flexget config with support of secrets file. <br> 
You only need to fill in your credentials. <br>
<br>
### Add:<br>
- Manual adding via trakt.tv Watchlist <br>
- Automatic adding via trakt_popular, trakt_trending and Ombi <br>
<br>
- merge any (Public) trakt list to own lists <br>
<br>
### Download:<br>
- perform search on multiple sites <br>
- perform daily crawl on multiple sites <br>
<br>
- Supported-Downloaders: JDownloader and pyLoad <br>
<br>
### Move:<br>
- Filebot-like file-moving and sorting of Library (coming soon) <br>

#### support-Forum<br>
https://board.jdownloader.org/showthread.php?t=67579  <br>

#
#### Best Multi-Hoster
[Premiumize](https://www.premiumize.me/ref/709558658) <br>
- Best All-In-One Provider (VPN, Torrent, Share-Hoster, cloud-space) <br>

 # Installation :
`sudo apt-get install unzip python python-beautifulsoup python3-bs4 python-pip` <br>
`sudo pip install --upgrade pip setuptools flexget rebulk lxml`<br>
<br>
`cd /tmp/ && wget https://github.com/crack00r/Flexget-Config/archive/master.zip`<br>
`unzip  master.zip`<br>
`mkdir ~/.flexget && cp -r Flexget-Config-master/* ~/.flexget/`<br>

`flexget trakt auth USER`<br>


<br>
Options.yml editieren - fertig.<br>
<br>
Anschließend per Cron oder Daemon starten:<br>
- `flexget execute` <br>
- `/usr/local/bin/flexget daemon start -d` (https://flexget.com/Daemon) <br>
