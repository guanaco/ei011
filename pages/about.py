# shirui.cheng@gmail.com
# about.html

from pages import TemplateHandler

class AboutHandler(TemplateHandler):
    def title(self):
        return "About"
    
    def main(self):
        return "about"