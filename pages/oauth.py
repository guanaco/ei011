# -*- coding: utf-8 -*-
# Copyright under  the latest Apache License 2.0

import logging
import StringIO
import gzip
from uuid import uuid4

import gtap
from gtap import TwitterClient
from pages import TemplateHandler

def compress_buf(buf):
    zbuf = StringIO.StringIO()
    zfile = gzip.GzipFile(None, 'wb', 9, zbuf)
    zfile.write(buf)
    zfile.close()
    return zbuf.getvalue()

class OauthHandler(TemplateHandler):

    def get(self, mode=""):
        callback_url = "%s/oauth/verify" % self.request.host_url
        client = TwitterClient(gtap.CONSUMER_KEY, gtap.CONSUMER_SECRET, callback_url)

        if mode=='session':
            # step C Consumer Direct User to Service Provider
            try:
                url = client.get_authorization_url()
                self.redirect(url)
            except Exception,error_message:
                self.response.out.write( error_message )


        if mode=='verify':
            # step D Service Provider Directs User to Consumer
            auth_token = self.request.get("oauth_token")
            auth_verifier = self.request.get("oauth_verifier")

            # step E Consumer Request Access Token 
            # step F Service Provider Grants Access Token
            try:
                access_token, access_secret, screen_name = client.get_access_token(auth_token, auth_verifier)
                self_key = '%s' % uuid4()
                # Save the auth token and secret in our database.
                client.save_user_info_into_db(username=screen_name, password=self_key, 
                                              token=access_token, secret=access_secret)
                show_key_url = '%s/oauth/showkey?name=%s&key=%s' % (
                                                                       self.request.host_url, 
                                                                       screen_name, self_key)
                self.redirect(show_key_url)
            except Exception,error_message:
                logging.debug("oauth_token:" + auth_token)
                logging.debug("oauth_verifier:" + auth_verifier)
                logging.debug( error_message )
                self.response.out.write( error_message )
        
        if mode=='showkey':
            screen_name = self.request.get("name")
            self_key = self.request.get("key")
            out_message = """
                <html><head><title>GTAP</title>
                <style>body { padding: 20px 40px; font-family: Courier New; font-size: medium; }</style>
                </head><body><p>
                your twitter's screen name : <b>#screen_name#</b> <br /><br />
                the Key of this API : <b>#self_key#</b> <a href="#api_host#/oauth/change?name=#screen_name#&key=#self_key#">you can change it now</a><br /><br />
                </p>
                <p>
                In the third-party client of Twitter which support Custom API address,<br />
                set the API address as <b>#api_host#/</b> or <b>#api_host#/api/1/</b> , <br />
                and set Search API address as <b>#api_host#/search/</b> . <br />
                Then you must use the <b>Key</b> as your password when Sign-In in these clients.
                </p></body></html>
                """
            out_message = out_message.replace('#api_host#', self.request.host_url)
            out_message = out_message.replace('#screen_name#', screen_name)
            out_message = out_message.replace('#self_key#', self_key)
            self.response.out.write( out_message )
        
        if mode=='change':
            screen_name = self.request.get("name")
            self_key = self.request.get("key")
            out_message = """
                <html><head><title>GTAP</title>
                <style>body { padding: 20px 40px; font-family: Courier New; font-size: medium; }</style>
                </head><body><p><form method="post" action="%s/oauth/changekey">
                your screen name of Twitter : <input type="text" name="name" size="20" value="%s"> <br /><br />
                your old key of this API : <input type="text" name="old_key" size="50" value="%s"> <br /><br />
                define your new key of this API : <input type="text" name="new_key" size="50" value=""> <br /><br />
                <input type="submit" name="_submit" value="Change the Key">
                </form></p></body></html>
                """ % (self.request.host_url, screen_name, self_key)
            self.response.out.write( out_message )
            
    def post(self, mode=''):
        
        callback_url = "%s/oauth/verify" % self.request.host_url
        client = TwitterClient(self.CONSUMER_KEY, self.CONSUMER_SECRET, callback_url)
        
        if mode=='changekey':
            screen_name = self.request.get("name")
            old_key = self.request.get("old_key")
            new_key = self.request.get("new_key")
            user_access_token, user_access_secret  = client.get_access_from_db(screen_name, old_key)
            
            if user_access_token is None or user_access_secret is None:
                logging.debug("screen_name:" + screen_name)
                logging.debug("old_key:" + old_key)
                logging.debug("new_key:" + new_key)
                self.response.out.write( 'Can not find user from db, or invalid old_key.' )
            else:
                try:
                    client.save_user_info_into_db(username=screen_name, password=new_key, 
                                                  token=user_access_token, secret=user_access_secret)
                    show_key_url = '%s/oauth/showkey?name=%s&key=%s' % (
                                                                        self.request.host_url, 
                                                                        screen_name, new_key)
                    self.redirect(show_key_url)
                except Exception,error_message:
                    logging.debug("screen_name:" + screen_name)
                    logging.debug("old_key:" + old_key)
                    logging.debug("new_key:" + new_key)
                    logging.debug( error_message )
                    self.response.out.write( error_message )
