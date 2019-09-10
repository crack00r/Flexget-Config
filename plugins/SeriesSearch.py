# -*- coding: utf-8 -*-
import logging, re, html.parser #, urllib, urllib2, json, requests

from flexget import plugin
from flexget.event import event

#import API
from .BaseSearchPlugin import BaseSearchPlugin
from .SerienjunkiesApi import SerienjunkiesApi

log = logging.getLogger(__name__)

class SearchSerienjunkies(BaseSearchPlugin):
    """
        Serienjunkies search plugin.
    """
    
    schema = {
        'type': 'object',
        'properties': {
            'hoster': {'type': 'string'},
            'language': {'type': 'string', 'enum': ['english', 'german']},
        },
        'additionalProperties': True
    }

    @plugin.internet(log)
    def search(self, task, entry, config):
        self.log = log
        
        api = SerienjunkiesApi( config, self.log )
        results = api.search(entry.get('search_strings', [entry['title']]))
        return self.create_entries(results)

@event('plugin.register')
def register_plugin():
    plugin.register(SearchSerienjunkies, 'searchSerienjunkies', interfaces=['search'], api_ver=2)
    
