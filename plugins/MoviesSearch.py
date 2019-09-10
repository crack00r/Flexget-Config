# -*- coding: utf-8 -*-
import logging, re #, urllib, urllib2, json, HTMLParser, requests

from flexget import plugin
from flexget.event import event

#import API
from .BaseSearchPlugin import BaseSearchPlugin
from .HDAreaApi import HDAreaApi
from .HDWorldApi import HDWorldApi
from .MovieBlogApi import MovieBlogApi



log = logging.getLogger(__name__)

class SearchHdarea(BaseSearchPlugin):
    """
        HD-Area search plugin.
    """

    @plugin.internet(log)
    def search(self, task, entry, config):
        self.log = log
        
        api = HDAreaApi( config, log )
        results = api.search(entry.get('search_strings', [entry['title']]))
        return self.create_entries(results)

class SearchHdworld(BaseSearchPlugin):
    """
        HD-World search plugin.
    """

    @plugin.internet(log)
    def search(self, task, entry, config):
        self.log = log
        
        api = HDWorldApi( config, log )
        results = api.search(entry.get('search_strings', [entry['title']]))
        return self.create_entries(results)

class SearchMovieBlog(BaseSearchPlugin):
    """
        MovieBlog search plugin.
        
        
        Bug:
        
        This Plugins raises a known Flexget issue:
        
        ## https://github.com/Flexget/Flexget/issues/847
        ## Solution:
        ## In flexget\plugins\input\discover.py's entry_complete method, insert:
        if entry not in search_results:
            # Rebuild search_results in place to recompute all its hashes
            search_results_copy = list(search_results)
            search_results.intersection_update([])      # empty search_results set in place
            search_results.update(search_results_copy)  # repopulate search_results set in place
            
        ##before the line:

        search_results.remove(entry)  
    """

    @plugin.internet(log)
    def search(self, task, entry, config):
        self.log = log
        
        api = MovieBlogApi( config, self.log )
        results = api.search(entry.get('search_strings', [entry['title']]))
        return self.create_entries(results)


## register plugins

@event('plugin.register')
def register_plugin():
    plugin.register(SearchHdarea, 'searchHdarea', interfaces=['search'], api_ver=2)
    
@event('plugin.register')
def register_plugin():
    plugin.register(SearchHdworld, 'searchHdworld', interfaces=['search'], api_ver=2)

@event('plugin.register')
def register_plugin():
    plugin.register(SearchMovieBlog, 'searchMovieBlog', interfaces=['search'], api_ver=2)
