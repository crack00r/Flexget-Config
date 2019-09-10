# -*- coding: utf-8 -*-
import logging, json, datetime, time
from flexget.entry import Entry

log = logging.getLogger(__name__)

class BaseSearchPlugin(object):
    config = {}
 
    schema = {
        'type': 'object',
        'properties': {
            'hoster': {'type': 'string'}
        },
        'additionalProperties': False
    }
    
    def create_entries(self, search_result_entries):
    
        entries = set()
        for search_result_entry in search_result_entries:
            for link in search_result_entry.getLinks():
                entry = Entry()
                entry['title'] = search_result_entry.getTitle()
                entry['url'] = link
                entry['imdb_url'] = search_result_entry.getImdbUrl() ##experimental
                
                if search_result_entry.getSize() > 0:
                    entry['content_size'] = search_result_entry.getSize()
                    
                self.log.verbose("Entry -> Title:"+ search_result_entry.getTitle()+", Link: " + link + ", Size: "+ str(search_result_entry.getSize()))
                entries.add(entry)

        return entries
        
    