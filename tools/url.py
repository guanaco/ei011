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
        self.fetched = urlfetch.fetch(url = url, deadline = 10)
        return self.status_ok()
        
    def getTitle(self):
        title = ""
        if self.status_ok():
            content = self.fetched.content
            title = content[(content.index("<title>") + len("<title>")):content.index("</title>")].decode("utf-8")
        return title