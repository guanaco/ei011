# shirui.cheng@gmail.com
# main.html

import urlparse, base64, logging
from cgi import parse_qsl
from google.appengine.api import urlfetch
from wsgiref.util import is_hop_by_hop

from pages import TemplateHandler
import gtap
from gtap import TwitterClient

class MainHandler(TemplateHandler):
    def title(self):
        return "Main"
    
    def main(self):
        return "main"

    def conver_url(self, orig_url):
        (scm, netloc, path, params, query, _) = urlparse.urlparse(orig_url)
        
        path_parts = path.split('/')
        
        if path_parts[1] == 'api' or path_parts[1] == 'search':
            sub_head = path_parts[1]
            path_parts = path_parts[2:]
            path_parts.insert(0,'')
            new_path = '/'.join(path_parts).replace('//','/')
            new_netloc = sub_head + '.twitter.com'
        else:
            new_path = path
            new_netloc = 'twitter.com'
    
        new_url = urlparse.urlunparse(('https', new_netloc, new_path.replace('//','/'), params, query, ''))
        return new_url, new_path

    def parse_auth_header(self, headers):
        username = None
        password = None
        
        if 'Authorization' in headers :
            auth_header = headers['Authorization']
            auth_parts = auth_header.split(' ')
            user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
            username = user_pass_parts[0]
            password = user_pass_parts[1]
    
        return username, password
    
    def gtap_error(self, content):
        self.ret = 503
        self.template["gtap_output"] = "<h3>gtap server error:</h3>%s"%(content)

    def process(self, method):
        orig_url = self.request.url
        orig_body = self.request.body

        new_url,new_path = self.conver_url(orig_url)

        if new_path == '/' or new_path == '':
            self.template["gtap_version"] = gtap.gtap_version
            return
        
        username, password = self.parse_auth_header(self.request.headers)
        user_access_token = None
        
        callback_url = "%s/oauth/verify" % self.request.host_url
        client = TwitterClient(gtap.CONSUMER_KEY, gtap.CONSUMER_SECRET, callback_url)

        if username is None :
            protected=False
            user_access_token, user_access_secret = '', ''
        else:
            protected=True
            user_access_token, user_access_secret  = client.get_access_from_db(username, password)
            if user_access_token is None :
                self.gtap_error("Can not find this user from db")
                return
        
        additional_params = dict([(k,v) for k,v in parse_qsl(orig_body)])

        use_method = urlfetch.GET if method=='GET' else urlfetch.POST

        try :
            data = client.make_request(url=new_url, token=user_access_token, secret=user_access_secret, 
                                   method=use_method, protected=protected, 
                                   additional_params = additional_params)
        except Exception,error_message:
            logging.debug(error_message)
            self.gtap_error(error_message)
        else :
            #logging.debug(data.headers)
            #self.response.headers.add_header('GTAP-Version', gtap_version)
            for res_name, res_value in data.headers.items():
                if is_hop_by_hop(res_name) is False and res_name!='status':
                    self.response.headers.add_header(res_name, res_value)
            self.template["gtap_output"] = data.content