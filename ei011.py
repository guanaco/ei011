#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

''' google app engine '''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.dist import use_library
use_library('django', '1.2')

''' my '''
from tools.xmpp import XMPPHandler
from pages.main import MainHandler
from pages.about import AboutHandler
from pages.history import HistoryHandler

application = webapp.WSGIApplication(
    [('/', MainHandler),
     ('/history', HistoryHandler),
     ('/about', AboutHandler),
     ('/_ah/xmpp/message/chat/', XMPPHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
