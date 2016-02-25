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

CATEGORIES = {
    # Hoster
    'Uploaded': "ul",
    'ShareOnline': "so",

    # Movies
    'BluRay 720p': 2,
    'BluRay 1080p': 5,
    'XviD': 15,
    'BRRip': 16,

    # TV
    'HDTV': 7,
    'SDTV': 24,
    'TV WEB-DL': 14
}


class SearchSerienjunkies(object):
    """
        Serienjunkies search plugin.

        To perform search against single category:

        publichd:
            category: BluRay 720p

        To perform search against multiple categories:

        publichd:
            category:
                - BluRay 720p
                - BluRay 1080p

        Movie categories accepted: BluRay 720p, BluRay 1080p, XviD, BRRip
        TV categories accepted: HDTV, SDTV, TV WEB-DL

        You can use also use category ID manually if you so desire (eg. BluRay 720p is actually category id '2')
    """

    schema = {
        'type': 'object',
        'properties': {
            'category': one_or_more({
                'oneOf': [
                    {'type': 'integer'},
                    {'type': 'string', 'enum': list(CATEGORIES)},
                ]})
        },
        "additionalProperties": False
    }

    @plugin.internet(log)
    def search(self, task, entry, config=None):
        """
            Search for entries on Serienjunkies
        """

#        categories = config.get('category', 'all')
        # Ensure categories a list
#        if not isinstance(categories, list):
#            categories = [categories]
        # Convert named category to its respective category id number
#        categories = [c if isinstance(c, int) else CATEGORIES[c] for c in categories]
#        category_url_fragment = '&category=%s' % urllib.quote(';'.join(str(c) for c in categories))

        base_url = 'http://serienjunkies.org/search/'
        mull = {"Dauer:", "Download:", "Uploader:", u"Größe:", u"Tonhöhe:", "Sprache:", "Format:", "HQ-Cover:"}

        entries = set()
        for search_string in entry.get('search_strings', [entry['title']]):
            query = normalize_unicode(search_string)
            query_url_fragment = urllib.quote(query.encode('utf8'))

            # http://serienjunkies.org/search/QUERY
            url = (base_url + query_url_fragment)
            log.debug('Serienjunkies search url: %s' % url)

            page = requests.get(url).content
            soup = get_soup(page)
            hoster = 'uploaded.to' # In "share-online.biz" ändern für anderen Hoster. Wird integriert in Flexget via config.yml. Im Moment nur manuell einstellbar
            for p in soup.find_all('p'):
                entry = Entry()
                if p.strong is not None and p.strong.text not in mull:
                    try:
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
