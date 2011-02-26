# shirui.cheng@gmail.com

""" common """
import os
from datetime import datetime

""" google app engine """
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

""" my """
from database import AuthenticatedUser
from database import Log
from im import XMPPHandler

class TemplateHandler(webapp.RequestHandler):
    def respond(self, content):
        self.response.out.write(content)
        
    def path(self, file):
        return os.path.join(os.path.dirname(__file__), "pages/%s.html"%(file))
        
    def process(self, method):
        pass

    def title(self):
        """ should define """
        pass

    """ {{ main }} part of the page """
    def main(self):
        """ should define """
        pass
    
    def init(self):
        self.user = ""
        self.ret = 200
        self.template = {"main": "", "title": self.title()}
        user = users.get_current_user()
        if user:
            authUsers = AuthenticatedUser.all()
            for tmpUser in authUsers:
                if tmpUser.jid == user.email():
                    self.user = tmpUser.type
                    greeting = "%s<a href=\"%s\">(logout)</a>"%(user.nickname(), users.create_logout_url("/"))
                    break
        else:
            greeting = "<a href=\"%s\">login</a>"%(users.create_login_url("/"))
            
        self.template["greeting"] = greeting
        self.template["now"] = datetime.now()
        
    def output(self):
        """ render {{ main }} """
        if self.user:
            if self.ret is not 200:
                self.response.set_status(self.ret)
            self.template["main"] += template.render(self.path(self.main()), self.template)
        
        """ render and respond page """
        self.respond(template.render(self.path("template"), self.template))
        
    def get(self):
        self.init()
        self.process("GET")
        self.output()
        
    def post(self):
        self.init()
        self.process("POST")
        self.output()
