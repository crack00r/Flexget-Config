# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import
import logging
import urllib
import re

from flexget import plugin
from flexget.entry import Entry
from flexget.event import event
from flexget.config_schema import one_or_more
from flexget.utils import requests
from flexget.utils.soup import get_soup
from flexget.utils.search import torrent_availability, normalize_unicode

log = logging.getLogger('searchSerienjunkies')

HOSTER = ['uploaded.to', 'share-online.biz']
LANGUAGE = ['english', 'german']

DEFHOS = 'uploaded.to'
DEFLANG = 'german'

#CATEGORIES = {
#    # Hoster
#    'Uploaded': "ul",
#    'ShareOnline': "so",
#
#    # Sprache
#    'Sprache': "deutsch",
#
#    # Movies
#    'BluRay 720p': 2,
#    'BluRay 1080p': 5,
#    'XviD': 15,
#    'BRRip': 16,
#
#    # TV
#    'HDTV': 7,
#    'SDTV': 24,
#    'TV WEB-DL': 14
#}


class SearchSerienjunkies(object):
    """
        Serienjunkies search plugin.
    """

    schema = {
        'type': 'object',
        'properties': {
            'language': {'type': 'string', 'enum': LANGUAGE},
            'hoster': {'type': 'string', 'enum': HOSTER}
        },
        'additionalProperties': False
    }

    @plugin.internet(log)
    def search(self, task, entry, config=None):
        """
            Search for entries on Serienjunkies
        """
        base_url = 'http://serienjunkies.org/search/'
        mull = {"Dauer:", "Download:", "Uploader:", u"Größe:", u"Tonhöhe:", "Sprache:", "Format:", "HQ-Cover:"}
        self.config = task.config.get('searchSerienjunkies') or {}
        self.config.setdefault('hoster', DEFHOS)
        self.config.setdefault('language', DEFLANG)

        entries = set()
        for search_string in entry.get('search_strings', [entry['title']]):
            query = normalize_unicode(search_string)
            query_url_fragment = urllib.quote(query.encode('utf8'))

            # http://serienjunkies.org/search/QUERY
            url = (base_url + query_url_fragment)
            log.debug('Serienjunkies search url: %s' % url)

            page = requests.get(url).content
            soup = get_soup(page)
            hoster = self.config['hoster']
            if self.config['language'] == 'english':
                english = True
            else:
                english = None
            for p in soup.find_all('p'):
                entry = Entry()
                if p.strong is not None and p.strong.text not in mull:
                  if english:
                    try:
                      if not p.strong.find(text=re.compile("german", flags=re.IGNORECASE)):
                        link = p.find(text=re.compile(hoster)).find_previous('a')
                        entry['title'] = p.strong.text
                        entry['url'] = link.get('href')
                        entries.add(entry)
                    except:
                      pass
                  else:
                    try:
                      if p.strong.find(text=re.compile("german", flags=re.IGNORECASE)):
                        link = p.find(text=re.compile(hoster)).find_previous('a')
                        entry['title'] = p.strong.text
                        entry['url'] = link.get('href')
                        entries.add(entry)
                    except:
                      pass
        return entries


@event('plugin.register')
def register_plugin():
    plugin.register(SearchSerienjunkies, 'searchSerienjunkies', groups=['search'], api_ver=2)
