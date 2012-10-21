#!/usr/local/bin/python

import os
import sys
import socket

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.web
import tornado.httpserver
import tornado.ioloop

import constants

from rayage_ws import WebSocketHandler
from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import admin_handlers

class RequestHandler(CASVerifiedRequestHandler):
    def get(self, action):
        if action == "logout":
            self.logout_user()
        else:
            if self.get_current_user() is None:
                self.validate_user()
                return
                
            if action == "admin":
                with open(system_directory+'/static/admin.html') as f:
                    self.write(f.read())
                    self.finish()
                    
                #self.write("Admin page<br>Logged in as %s!<br><a href=\"/logout\">logout</a>" % self.get_current_user())
                #self.finish()
            else:
                with open(system_directory+'/static/index.html') as f:
                    self.write(f.read())
                    self.finish()

handlers = [
    (r'/(admin|logout|)', RequestHandler),
    (r'/(.*\.js|welcome\.html)', tornado.web.StaticFileHandler, {'path': system_directory+'/static'}),
    (r'/codemirror/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/codemirror'}),
    (r'/custom/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/custom'}),
    (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/images'}),
    (r'/styles/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/styles'}),
    (r'/ws', WebSocketHandler),
]

if __name__ == "__main__":
        tornado_app = tornado.web.Application(handlers, cookie_secret=constants.COOKIE_SECRET)
        
        tornado_http = tornado.httpserver.HTTPServer(tornado_app, ssl_options= {"certfile": "misc/server.crt", "keyfile": "misc/server.key"})
        tornado_http.bind(8080, family=socket.AF_INET)
        tornado_http.start()
        tornado.ioloop.IOLoop.instance().start()
