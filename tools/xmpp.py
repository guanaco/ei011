# shirui.cheng@gmail.com

""" google app engine """
from google.appengine.api import xmpp
from google.appengine.ext import webapp

""" my """
from database import AuthenticatedUser
from database import Log
from timezone import GetTimezoneSet
from timezone import GetTimezoneString
from timezone import OutputDatatime

class Command(object):
    def __init__(self, type, name, handler, help):
        try:
            self.__type = type
            self.__name = name
            self.__handler = handler
            self.__help = help
        except KeyError, e:
            raise xmpp.InvalidMessageError(e[0])
    
    @property
    def type(self):
        return self.__type
    
    @property
    def name(self):
        return self.__name
    
    @property
    def handler(self):
        return self.__handler
    
    @property
    def help(self):
        return self.__help

class XMPPHandler(webapp.RequestHandler):
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.users = AuthenticatedUser.all()
        self.cmds = [
                      Command("all",    "help", self.commandHelp,           "@help")
                     ,Command("admin",  "invite", self.commandInvite,       "@invite id@dot.com [admin|user]")
                     ,Command("admin",  "kick", self.commandKick,           "@kick id@dot.com")
                     ,Command("user",   "history", self.commandHistory,     "@history [0~100]")
                     ,Command("user",   "names", self.commandNames,         "@names")
                     ,Command("user",   "timezone", self.commandTimezone,   "@timezone %s"%(GetTimezoneString()))
                     ]
        self.Num2SendOnce = 200
        self.indexLast = -1
        
    def post(self):
        msg = ""
        message = xmpp.Message(self.request.POST)
        sender = self.stripJidResource(message.sender)
        if self.isCommand(message.body):
            msg = self.handleCommand(sender, message.body[1:])
        else:
            if self.isAuthenticated(sender):
                self.send2Others(sender, "<%s..>: %s"%(self.stripJidDomain(sender), message.body))
                if self.indexLast < 0:
                    self.indexLast = Log.GetLastIndex() + 1
                log = Log(index=self.indexLast, jid=sender, msg=message.body)
                log.put()
            else:
                msg = "you are not authorized to send msg in this group."
            
        if msg != "":
            message.reply(msg)
            
    def getUser(self, jid):
        for u in self.users:
            if u.jid == jid:
                return u
            
    def send2Others(self, sender, msg):
        for u in self.users:
            if sender != u.jid:
                self.send2One(u.jid, msg)
                
    def buildMsg(self, i, msg):
        ret = "(%d-%d)%s"%(i, i + len(msg), msg)
        if not i and len(msg) < self.Num2SendOnce:
            ret = msg
        return ret
            
    def send2One(self, jid, msg):
        if xmpp.get_presence(jid):
            i = 0
            while len(msg[i:]) > self.Num2SendOnce:
                xmpp.send_message(jid, self.buildMsg(i, msg[i:i+self.Num2SendOnce]))
                i += self.Num2SendOnce
            if i < len(msg):
                xmpp.send_message(jid, self.buildMsg(i, msg[i:]))
        
    def stripJidResource(self, jid):
        return jid[:jid.index("/")]
    
    def stripJidDomain(self, jid):
        return jid[:jid.index("@")]
        
    def isCommand(self, msg):
        return msg[0] == "@"
    
    def commandInvite(self, sender, payload):
        target = payload[1]
        type = "user"
        if len(payload) > 2:
            if payload[2] in ["admin", "user"]:
                type = payload[2]
        xmpp.send_invite(target)
        u = AuthenticatedUser(key_name=target, jid=target, type=type)
        u.put()
        self.users = AuthenticatedUser.all()
        self.send2One(target, "you are added by %s as %s."%(sender, type))
        return "%s invited to list."%(target)
    
    def commandKick(self, sender, payload):
        target = payload[1]
        AuthenticatedUser.Remove(target)
        self.users = AuthenticatedUser.all()
        self.send2One(target, "you are deleted by %s."%(sender))
        return "%s kicked from list."%(target)
    
    def commandHelp(self, sender, payload):
        ret = "http://ei011-bot.appspot.com\navailable commands:\n"
        for c in self.cmds:
            toAdd = True
            if c.type == "admin" and not self.isAdmin(sender):
                toAdd = False
            elif c.type == "user" and not self.isAuthenticated(sender):
                toAdd = False
            if toAdd:
                ret += "%s\n"%(c.help)
        return ret
    
    def commandHistory(self, sender, payload):
        num = 10
        if len(payload) > 1:
            try:
                num = int(payload[1])
            except:
                return "invalid payload \"%s\""%(payload[1])
        if num > 100:
            num = 100
        msgs = Log.QueryByNum(num)
        num = msgs.count(num)
        str = "== history %d begin ==\n"%(num)
        timezone = self.getUser(sender).timezone
        for i in range(0, num):
            jid = msgs[i].jid
            jid = jid[:jid.index("@")]
            str += "[%s]%s..: %s\n"%(OutputDatatime(msgs[i].timestamp, timezone), jid, msgs[i].msg)
        str += "== history %d end ==\n"%(num)
        self.send2One(sender, str)
        return ""
    
    def commandNames(self, sender, payload):
        ret = ""
        online = 0
        for j in self.users:
            if xmpp.get_presence(j.jid):
                ret += "ONLINE"
                online += 1
            else:
                ret += "offline"
            ret += ": %s\n"%(j.jid)
        return "Online: %d\n%s"%(online, ret)
    
    def commandTimezone(self, sender, payload):
        ret = "Invalid user id %s"%(sender)
        user = self.getUser(sender)
        if user:
            if payload in GetTimezoneSet():
                user.timezone = payload
                user.put()
                ret = "Timezone set to %s"%(payload)
            else:
                ret = "Invalid timezone %s, valid options are:%s"%(payload, GetTimezoneString())
        return ret
    
    def handleCommand(self, sender, cmd):
        words = cmd.split()
        ret = "invalid command %s."%(words[0])
        handle = False
        for c in self.cmds:
            if c.name == words[0]:
                #handle admin command
                if c.type == "admin":
                    if len(words) <= 1:
                        ret = "null payload."
                        break
                    if self.isAdmin(sender):
                        handle = True
                    else:
                        ret = "you(%s) could not perform @%s command."%(self.getUserType(sender), c.name)
                elif c.type == "all":
                    handle = True
                elif c.type == "user":
                    if self.isAuthenticated(sender):
                        handle = True
                break
        if handle:
            ret = c.handler(sender, words)
        return ret

    def isAdmin(self, jid):
        return self.getUserType(jid) == "admin"
    
    def isAuthenticated(self, jid):
        return self.getUserType(jid) in ["admin", "user"]

    def getUserType(self, jid):
        for u in self.users:
            if u.jid == jid:
                return u.type
        return None