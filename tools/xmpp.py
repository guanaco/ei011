#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shirui.cheng@gmail.com

""" google app engine """
from google.appengine.api import xmpp
from google.appengine.ext import webapp

""" my """
from database import AuthenticatedUser
from database import Log
from database import Share
from timezone import GetTimezones
from timezone import GetTimezoneString
from timezone import OutputDatetime
from url import UrlParser

class XMPPHandler(webapp.RequestHandler):
    class Command(object):
        def __init__(self, type, name, handler, argnum, help):
            try:
                self.__type = type
                self.__name = name
                self.__handler = handler
                self.__argnum = argnum
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
        
        @property
        def argnum(self):
            return self.__argnum

    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.users = AuthenticatedUser.all()
        self.cmds = [
                      XMPPHandler.Command("all",    "help", self.commandHelp,           0,  "@help")
                     ,XMPPHandler.Command("admin",  "invite", self.commandInvite,       1,  "@invite id@dot.com [ admin | user ]")
                     ,XMPPHandler.Command("admin",  "kick", self.commandKick,           1,  "@kick id@dot.com")
                     ,XMPPHandler.Command("user",   "history", self.commandHistory,     0,  "@history ( 0 ~ 100 )")
                     ,XMPPHandler.Command("user",   "names", self.commandNames,         0,  "@names")
                     ,XMPPHandler.Command("user",   "timezone", self.commandTimezone,   1,  "@timezone %s"%(GetTimezoneString()))
                     ,XMPPHandler.Command("user",   "share", self.commandShare,         1,  "@share (url)")
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
        target = payload[0]
        type = "user"
        if len(payload) > 1:
            if payload[1] in ["admin", "user"]:
                type = payload[1]
        xmpp.send_invite(target)
        u = AuthenticatedUser(key_name=target, jid=target, type=type)
        u.put()
        self.users = AuthenticatedUser.all()
        self.send2One(target, "you are added by %s as %s."%(sender, type))
        return "%s invited to list."%(target)
    
    def commandKick(self, sender, payload):
        target = payload[0]
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
        if len(payload) > 0:
            try:
                num = int(payload[0])
            except:
                return "invalid payload \"%s\""%(payload[0])
        if num > 100:
            num = 100
        msgs = Log.QueryByNum(num)
        num = msgs.count(num)
        str = "== history %d begin ==\n"%(num)
        timezone = self.getUser(sender).timezone
        for i in range(0, num):
            str += "[%s]%s..: %s\n"%(OutputDatetime(msgs[i].timestamp, timezone), self.stripJidDomain(msgs[i].jid), msgs[i].msg)
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
        user = AuthenticatedUser.GetUser(sender)
        tz = payload[0]
        if user:
            if tz in GetTimezones():
                user.timezone = tz
                user.put()
                ret = "Timezone set to %s"%(tz)
            else:
                ret = "Invalid timezone %s, valid options are:%s"%(tz, GetTimezoneString())
        return ret
    
    def commandShare(self, sender, payload):
        url = payload[0]
        ret = "failed to fetch url:%s"%(url)
        parser = UrlParser()
        if parser.open(url):
            title = parser.getTitle()
            index = Share.GetLastIndex() + 1
            share = Share(index = index, jid = sender, url = url, title = title)
            share.put()
            msg = "%s just shared %s|%s"%(self.stripJidDomain(sender), title, url)
            self.send2Others(sender, msg)
            ret = "share %s|%s success."%(title, url)
        return ret
    
    def handleCommand(self, sender, cmd):
        words = cmd.split()
        if len(words) <= 0:
            return "no command inputed."
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
        if handle and len(words[1:]) >= c.argnum:
            ret = c.handler(sender, words[1:])
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