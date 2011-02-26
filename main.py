# shirui.cheng@gmail.com

""" common """
import os
from datetime import datetime

""" google app engine """
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

""" my """
from database import AuthenticatedUser
from database import Log
from im import XMPPHandler

""" twitter """
from twitter import OAuthHandler
from twitter import OAuthClient

DEF_HIS_PER_PAGE = 20
MAX_HIS_PER_PAGE = 50

class RequestHandler(webapp.RequestHandler):
    def respond(self, content):
        self.response.out.write(content)
        
    def path(self, file):
        return os.path.join(os.path.dirname(__file__), "pages/%s.html"%(file))
        
    def process(self):
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
        
    def display(self):
        """ render {{ main }} """
        if self.user:
            self.template['main'] = template.render(self.path(self.main()), self.template)
        """ render and respond page """
        self.respond(template.render(self.path("template"), self.template))
        
    def get(self):
        self.init()
        self.process()
        self.display()

class MainHandler(RequestHandler):
    def title(self):
        return "Main"
    
    def main(self):
        return "main"
    
    def process(self):
        client = OAuthClient("twitter", self)
        if client.get_cookie():
            info = client.get('/account/verify_credentials')
            self.template["name"] = info["screen_name"]
            self.template["location"] = info["location"]
            self.template["rate"] = client.get('/account/rate_limit_status')
    
class AboutHandler(RequestHandler):
    def title(self):
        return "About"
    
    def main(self):
        return "about"

class HistoryHandler(RequestHandler):
    def title(self):
        return "History"
    
    def main(self):
        return "history"
            
    def parseNum(self):
        num = DEF_HIS_PER_PAGE
        numStr = self.request.get("num")
        if numStr:
            try:
                num = int(numStr)
                if num < 0:
                    num = DEF_HIS_PER_PAGE
                elif num > MAX_HIS_PER_PAGE:
                    num = MAX_HIS_PER_PAGE
            except:
                pass
        return num
                
    def parseOffset(self):
        offset = 0
        offsetStr = self.request.get("offset")
        if offsetStr:
            offset = int(offsetStr)
        return offset
            
    def parseDirection(self):
        return self.request.get("direction")
                                   
    def process(self):
        num = self.parseNum()
        offset = self.parseOffset()
        direction = self.parseDirection()
        
        last = Log.GetLastIndex() + 1
        if direction == "prev":
            if offset + num < last:
                offset += num
        elif direction == "next":
            if offset - num >= 0:
                offset -= num

        start = last - num - offset
        if start < 0:
            start = 0
        end = start + num
        if end > last:
            end = last
        logs = Log.QueryByIndex(start, end)
        
        self.template["prev"] = ((offset + num) < last)
        self.template["next"] = ((offset - num) >= 0)
        self.template["offset"] = offset
        self.template["num"] = num
        self.template["last"] = last - 1
        self.template["logs"] = logs

application = webapp.WSGIApplication(
    [("/", MainHandler),
     ("/history", HistoryHandler),
     ("/about", AboutHandler),
     ('/oauth/(.*)/(.*)', OAuthHandler),
     ("/_ah/xmpp/message/chat/", XMPPHandler)],
    debug=True)

def main():
    csr = AuthenticatedUser(key_name="shirui.cheng@gmail.com", jid="shirui.cheng@gmail.com", type="admin")
    csr.put()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
