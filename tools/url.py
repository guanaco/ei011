#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

from google.appengine.api import urlfetch

class UrlParser:
    def __init__(self):
        self.fetched = None
        
    def status_ok(self):
        try: 
            return self.fetched.status_code == 200
        except:
            return False
        
    def open(self, url):
        try:
            self.fetched = urlfetch.fetch(url = url, deadline = 10)
        except:
            pass
        return self.status_ok()
        
    def getTitle(self):
        title = ""
        if self.status_ok():
            content = self.fetched.content
            title = content[(content.index("<title>") + len("<title>")):content.index("</title>")].decode(self.getCharset())
        return title
    
    def getCharset(self):
        charset = "utf-8"
        if self.status_ok():
            content = self.fetched.content
            while len(content):
                """ search <meta ...> """
                start = content.index("<meta ")
                end = content[start:].index(">")
                meta = content[start:end]
                try:
                    i = meta.index("charset=") + len("charset=")
                    j = meta[i:].index("\"")
                    charset = meta[i:j].lower()
                    break
                except:
                    content = content[end+1:]
        return charset