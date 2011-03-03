#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

import logging
import urllib2
import re

class HtmlChecker:
    def __init__(self, line, pattern, collector):
        self.pattern = pattern
        self.collector = collector
    
    @property
    def pattern(self):
        return self.pattern
    
    @property
    def collector(self):
        return self.collector

class UrlParser:
    def __init__(self):
        self.title = None
        self.charset = None
        self.checkers = {
                          HtmlChecker('<\stitle\s>*</\stitle\s>', self.title)
                         ,HtmlChecker(('<\s*meta[^>]+charset=([^>]*?)[;\'">]', re.I), self.charset)
                         }
        
    def log(self, msg):
        logging.debug('--- csr ---:%s'%(msg))
        
    def fixUrl(self, url):
        if url[:'https://'] not in ['http://', 'https://']:
            url = 'http://'+url
            
    def check(self, line, checker):
        ret = None
        regexp = re.compile(checker.pattern)
        found = regexp.search(line)
        if found:
            ret = found.groups()[0]
            try:
                ret = ret.lower()
            except:
                pass
        checker.collector = ret
        return ret is not None
        
    def open(self, url):
        req = urllib2.urlopen(self.fixUrl(url))
        found = 0
        for line in req.readlines():
            for c in self.checkers:
                self.check(line, c)
            
    @property
    def title(self):
        return self.title