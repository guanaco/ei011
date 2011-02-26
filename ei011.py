# shirui.cheng@gmail.com


""" google app engine """
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

""" my """
from database import AuthenticatedUser
from im import XMPPHandler
from pages.main import MainHandler
from pages.about import AboutHandler
from pages.history import HistoryHandler
from pages.oauth import OauthHandler

application = webapp.WSGIApplication(
    [("/", MainHandler),
     ("/history", HistoryHandler),
     ("/about", AboutHandler),
     ("/oauth/", OauthHandler),
     ("/_ah/xmpp/message/chat/", XMPPHandler)],
    debug=True)

def main():
    csr = AuthenticatedUser(key_name="shirui.cheng@gmail.com", jid="shirui.cheng@gmail.com", type="admin")
    csr.put()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
