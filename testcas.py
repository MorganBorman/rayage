#!/usr/bin/env python

import os
import sys

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.httpserver
import tornado.ioloop
import tornado.web
import base64
import socket
import uuid
import urllib2
import xml.etree.ElementTree

from VerifiedHTTPSHandler import VerifiedHTTPSHandler

class RequestHandler(tornado.web.RequestHandler):
    def get(self, line):
        
        cas_server  = "https://websso.wwu.edu:443"
        service_url = "https://localhost:8080/"
    
        session_cookie = self.get_secure_cookie("test_cas_session_cookie")
        
        if self.get_argument('logout', default=None):
            self.clear_cookie("test_cas_session_cookie")
            self.redirect(cas_server + "/cas/logout", permanent=False)
            
        elif session_cookie is not None:
            print "session_cookie =", session_cookie
            self.write("Logged in!<br><a href=\"?logout=1\">logout</a>")
            self.finish()
            
        elif self.get_argument('ticket', default=None):
            #need to validate ticket
            ticket = self.get_argument('ticket')
            
            #generate URL for ticket validation 
            cas_validate = cas_server + "/cas/serviceValidate?ticket=" + ticket + "&service=" + service_url
            #f_xml_assertion = urllib.urlopen(cas_validate)
            
            https_handler = VerifiedHTTPSHandler()
            url_opener = urllib2.build_opener(https_handler)
            
            try:
                f_xml_assertion = url_opener.open(cas_validate)
            except urllib2.URLError:
                self.write("Error validating certificate of CAS server.")
                self.finish()
                return
            
            if not f_xml_assertion:
                print 'Unable to authenticate: trouble retrieving assertion from CAS to validate ticket.'
                self.send_error(status_code=401)
                return

            #parse CAS XML assertion into a ElementTree
            assertion_tree = xml.etree.ElementTree.parse(f_xml_assertion)
            if not assertion_tree:
                print 'Unable to authenticate: trouble parsing XML assertion.'
                self.send_error(status_code=401)
                return
            
            user_name = None
            wid = None
            #find <cas:user> in ElementTree
            for e in assertion_tree.iter():
                #print "DEBUG: Found tag '%s'" % e.tag
                if e.tag == "{http://www.yale.edu/tp/cas}user":
                    user_name = e.text
                elif e.tag == "{http://www.yale.edu/tp/cas}wid":
                    wid = e.text
                
            #close the handle to the ticket assertion
            f_xml_assertion.close()
                
            print "Got validation: user=%s wid=%s" %(user_name, wid)
                
            if not user_name or not wid:
                #couldn't find <cas:user> in the tree
                print 'Unable to validate ticket: could not locate cas:user element.'
                self.send_error(status_code=401)
                return
                
            self.set_secure_cookie("test_cas_session_cookie", user_name)
            
            self.redirect(service_url, permanent=False)
        else:
            self.redirect(cas_server + "/cas/login?service=" + service_url, permanent=False)

handlers = [        
    (r"/(.*)", RequestHandler),
]

#cookie_secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
cookie_secret = "g9Usc0wTSMWxV5a7G5o5YcXPb3ftcUBwhUoFT62KJks="

if __name__ == "__main__":
        tornado_app = tornado.web.Application(handlers, cookie_secret=cookie_secret)
        
        tornado_http = tornado.httpserver.HTTPServer(tornado_app, ssl_options= {"certfile": "misc/server.crt", "keyfile": "misc/server.key"})
        tornado_http.bind(8080, family=socket.AF_INET)
        tornado_http.start()
        tornado.ioloop.IOLoop.instance().start()
