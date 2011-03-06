#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com
# about.html

from pages.template import TemplateHandler

class AboutHandler(TemplateHandler):
    def title(self):
        return 'About'
    
    def main(self):
        return 'about'
    
    def process(self, method):
        self.template['about'] = [
            'TODO',
                ['Twitter proxy? pended.',
                 'share and browsing shared on the web',
                 'command shotcut'],
            'version 1.1 @ 2011-3.6',
                ['added @share command in xmpp',],
            'version 1.0 @ 2011-3-1',
                ['browser chat history for authenticated users',
                 'display chat log time in required timezone',],
            ]