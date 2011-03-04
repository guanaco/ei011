#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

import logging
import urllib2
import re

class HtmlChecker:
    def __init__(self, pattern, flag, collector):
        self.pattern = pattern
        self.flag = flag
        self.collector = collector

class UrlParser:
    def __init__(self):
        self.checkers = {
                          'title': HtmlChecker('<\s*title\s*>.*?</\s*title\s*>', 0, None)
                         ,'charset': HtmlChecker('<\s*meta[^>]+charset=([^>]*?)[;\'">]', re.I, None)
                        }
        
    def log(self, msg):
        logging.debug('--- csr ---:%s'%(msg))
        
    def fixUrl(self, url):
        if url[:len('https://')] not in ['http://', 'https://']:
            url = 'http://'+url
        return url
            
    def check(self, line, checker):
        ret = None
        regexp = re.compile(checker.pattern, checker.flag)
        found = regexp.search(line)
        if found:
            ret = found.groups()[0]
        checker.collector = ret
        return ret is not None
    
    def convertTitle(self):
        charset = 'utf-8'
        if self.checkers['charset'].collector:
            charset = self.checkers['charset'].collector.lower()
            self.log('using detected encoding %s.'%(charset))
        if self.checkers['title'].collector:
            self.checkers['title'].collector = self.checkers['title'].collector.decode(charset, 'ignore')
        
    def process(self, url):
        url = self.fixUrl(url)
        req = urllib2.urlopen(url)
        if req:
            found = 0
            for line in req.readlines():
                for k, c in self.checkers.items():
                    if self.check(line, c):
                        found += 1
                        self.log('found %s: %s'%(k, c.collector))
                if found > len(self.checkers):
                    ''' process done '''
                    break
        self.convertTitle()
        return req is not None, url
        
    @property
    def title(self):
        return self.checkers['title'].collector