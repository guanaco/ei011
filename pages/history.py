# shirui.cheng@gmail.com
# history.html

from database import Log
from pages import TemplateHandler

DEF_HIS_PER_PAGE = 20
MAX_HIS_PER_PAGE = 50

class HistoryHandler(TemplateHandler):
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
                                   
    def process(self, method):
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
