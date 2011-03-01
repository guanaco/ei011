# shirui.cheng@gmail.com

""" common """
import os
from datetime import datetime

""" google app engine """
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

""" my """
from tools.database import AuthenticatedUser
from tools.timezone import GetTimezoneInfo
from tools.timezone import DEFAULT_TZINFO

class TemplateHandler(webapp.RequestHandler):
    def respond(self, content):
        self.response.out.write(content)
        
    def path(self, file):
        return os.path.join(os.path.dirname(__file__), "%s.html"%(file))
        
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
        self.user = None
        self.ret = 200
        self.template = {"main": "", "title": self.title()}
        user = users.get_current_user()
        if user:
            for tmpUser in AuthenticatedUser.all():
                if tmpUser.jid == user.email():
                    self.user = tmpUser
                    greeting = "%s<a href=\"%s\">(logout)</a>"%(user.nickname(), users.create_logout_url("/"))
                    break
        else:
            greeting = "<a href=\"%s\">login</a>"%(users.create_login_url("/"))
            
        self.template["greeting"] = greeting
        tzinfo = DEFAULT_TZINFO
        if self.user:
            tzinfo = GetTimezoneInfo(self.user.timezone)
        now = datetime.now(tzinfo)
        self.template["now"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.template["tz"] = tzinfo.tzname(now)
        
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
