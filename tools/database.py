# shirui.cheng@gmail.com

from google.appengine.ext import db

from timezone import DEFAULT_TZ
from timezone import GetTimezoneSet

class AuthenticatedUser(db.Model):
    jid = db.StringProperty(required=True)
    type = db.StringProperty(required=True, choices=set(["admin","user"]))
    timezone = db.StringProperty(required=True, default=DEFAULT_TZ, choices=GetTimezoneSet())
    
    @classmethod
    def GetAdmins(cls):
        return db.Query(cls).filter("type =", "admin")
    
    @classmethod
    def Remove(cls, target):
        query = db.Query(cls).filter("jid =", target)
        db.delete(query)
  
class Log(db.Model):
    index = db.IntegerProperty(default = -1, required=True)
    jid = db.StringProperty(required=True)
    msg = db.TextProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def GetLastIndex(cls):
        return db.Query(cls).order("-index").get().index
    
    @classmethod
    def QueryByNum(cls, num):
        lastIndex = cls.GetLastIndex()
        return db.Query(cls).order("index").filter("index >", lastIndex - num)
    
    @classmethod
    def QueryByIndex(cls, start, end):
        return db.Query(cls).order("index").filter("index >=", start).filter("index <=", end)

    @property
    def nickname(self):
        return self.jid[:self.jid.index("@")]