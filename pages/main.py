#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com
# main.html

from pages.template import TemplateHandler

class MainHandler(TemplateHandler):
    def title(self):
        return "Main"
    
    def main(self):
        return "main"