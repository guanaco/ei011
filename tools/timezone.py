# shirui.cheng@gmail.com

import datetime

class UtcTzinfo(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(0)
    def dst(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'UTC'
    def olsen_name(self): return 'UTC'

class CstTzinfo(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(hours=+8)
    def dst(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'CST+08'
    def olsen_name(self): return 'China'

class PstTzinfo(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(hours=-8)
    def dst(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'PST+08PDT'
    def olsen_name(self): return 'US/Pacific'

TZINFOS = {
  'UTC(GMT)':   UtcTzinfo(),
  'CST(GMT+8)': CstTzinfo(),
  'PST(GMT-8)': PstTzinfo(),
}

DEFAULT_TZ = "CST(GMT+8)"
DEFAULT_TZINFO = UtcTzinfo()

def GetTimezoneSet():
    return set(TZINFOS.keys())

def GetTimezones():
    return TZINFOS.keys()

def GetTimezoneString():
    ret = ""
    for key in TZINFOS.keys():
        ret += "%s "%(key)
    return ret

def GetTimezoneInfo(name):
    return TZINFOS[name]

def OutputDatetime(dt, tzName):
    return dt.replace(tzinfo=DEFAULT_TZINFO).astimezone(GetTimezoneInfo(tzName)).strftime("%Y-%m-%d %H:%M:%S")