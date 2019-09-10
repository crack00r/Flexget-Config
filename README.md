
# Flexget-Config

Flexget-Config by snickers<br>
thanks to [topy](https://github.com/topy) for Plugins <br>

Mainly for German Users, but help with other languages is appreciated <br>
<br>
### Easy to use Flexget config with support of secrets file. <br>  You only need to fill in your credentials. <br>
<br>

### Add: <br>
- Manual adding via trakt.tv Watchlist <br>
- trakt_popular <br>
- trakt_trending <br>
- Ombi <br>
- merge any (Public) trakt list to own lists <br>
<br>

### Download:<br>
- perform search on multiple sites <br>
- perform daily crawl on multiple sites <br>
- Supported-Downloaders: JDownloader and pyLoad <br>
<br>

### Move:<br>
- Filebot-like file-moving and sorting of Library (coming soon) <br>

#### support-Forum<br>
https://board.jdownloader.org/showthread.php?t=67579  <br>

#
#### Best Multi-Hoster
[Premiumize](https://www.premiumize.me/ref/709558658) <br>
- Best All-In-One Provider (unlimited VPN, unlimited-Torrent, Share-Hoster, 1TB cloud-space and more) <br>

 # Installation :
`sudo apt-get install unzip python python-beautifulsoup python3-bs4 python-pip python3` <br>
`sudo pip install --upgrade pip setuptools flexget rebulk lxml subliminal`<br>
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
