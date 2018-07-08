# Flexget-Config

Flexget-Config by snickers<br>
thanks to [topy](https://github.com/topy) for Plugins <br>


Easy to use Flexget config with support of secrets file. You only need to fill in your credentials. <br>
Mainly for German Users <br>


### support-Forum<br>
https://board.jdownloader.org/showthread.php?t=67579  <br>

#
#### Best Multi-Hoster
[Premiumize](https://www.premiumize.me/ref/709558658) <br>
- Best All-In-One Provider (VPN, Torrent, Share-Hoster, cloud-space) <br>

[DebridItalia](http://www.debriditalia.com/?ref=ref68473) <br>
- Cheapest UNLIMITED-Traffic for Uploaded.to<br>


#### Donations / Spenden:
bitcoin: 12vHS4h6patf4Ne6og4BHcDxRma3g2URUK  <br>
Paypal: paypal.me/MadK <br>



 # Installation :
`sudo apt-get install unzip python python-beautifulsoup python3-bs4 python-pip` <br>
`sudo pip install --upgrade pip setuptools flexget guessit rebulk BeautifulSoup4 imdbpy`<br>
<br>
`cd /tmp/ && wget https://github.com/crack00r/Flexget-Config/archive/master.zip`<br>
`unzip  master.zip`<br>
`mkdir ~/.flexget && cp -r master/* ~/.flexget/`<br>

`flexget trakt auth USER`<br>


<br>
Options.yml editieren - fertig.<br>
<br>
Anschließend per Cron oder Daemon starten:<br>
- `flexget execute` <br>
- `/usr/local/bin/flexget daemon start -d` (https://flexget.com/Daemon) <br>
