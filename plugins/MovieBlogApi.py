# -*- coding: utf-8 -*-
import logging, re #, urllib, urllib2, json, HTMLParser, requests
from flexget.utils.tools import parse_filesize

from .BaseApi import BaseApi, SearchResultEntry
from .HDWorldApi import HDWorldApi

class MovieBlogApi(HDWorldApi):
    """
        MovieBlog Api.
    """
    
    def reset(self):
        self.search_query_url = 'http://www.movie-blog.org'
        self.search_query_static = {"cat":0,"page":1}
        self.search_query_param = "s"
        self.search_param_as_folder = ["page"]
        
        self.feed_query_url = "http://www.movie-blog.org"
        self.feed_query_static = {"page":1,"category":""}
        self.feed_query_category = "category"
        self.feed_query_page = "page"
        self.feed_param_as_folder = ["category","page"]
    
    html_entry_class = "beitrag"
    html_entry_title_element = "h1"
    html_entry_inner_class = "beitrag"
    
    html_feed_class = "beitrag2"

    def find_next_link(self, page):
        return page.find("a", {"class":"nextpostslink"})
