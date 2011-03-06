#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

import urllib2
import re

from debug import dbg

class HtmlChecker:
    def __init__(self, name, pattern, flag, collector):
        self.name = name
        self.pattern = pattern
        self.flag = flag
        self.collector = collector

class UrlParser:
    def __init__(self):
        self.titleChecker = HtmlChecker('title', '<\s*title\s*>(.*?)</\s*title\s*>', re.IGNORECASE, None)
        self.encodingChecker = HtmlChecker('encoding', '<\s*meta[^>]+charset=([^>]*?)[;\'">]', re.IGNORECASE, None)
        
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
            
    def search(self, url, checker, encoding=None):
        found = False
        try:
            req = urllib2.urlopen(url)
            for line in req.readlines():
                if encoding:
                    line = line.decode(encoding, 'replace')
                found = self.check(line, checker)
                if found:
                    dbg(checker.name+' found: '+checker.collector)
                    break
            req.close()
        except:
            pass
        return found
        
    def process(self, url):
        url = self.fixUrl(url)
        self.search(url, self.encodingChecker)
        encoding = 'utf-8'
        if self.encodingChecker.collector:
            encoding = self.encodingChecker.collector.lower()
        return self.search(url, self.titleChecker, encoding), url
        
    @property
    def title(self):
        return self.titleChecker.collector