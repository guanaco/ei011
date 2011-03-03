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