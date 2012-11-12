#!/usr/local/bin/python

import os
import sys
import socket

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.web
import tornado.httpserver
import tornado.ioloop

import database
import constants

from database.User import User

from rayage_ws import WebSocketHandler
from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import editor_handlers
import admin_handlers

class RequestHandler(CASVerifiedRequestHandler):
    def get(self, action):
        if action == "logout":
            self.logout_user()
        else:
            username = self.get_current_user()
            
            if username is None:
                self.validate_user()
                return
                
            user = User.get_user(username)
                
            if action == "admin" and user.permission_level >= constants.PERMISSION_LEVEL_TA:
                with open(system_directory+'/static/admin.html') as f:
                    self.write(f.read())
                    self.finish()
            elif user.permission_level >= constants.PERMISSION_LEVEL_USER:
                with open(system_directory+'/static/index.html') as f:
                    self.write(f.read())
                    self.finish()
            else:
                with open(system_directory+'/static/denied.html') as f:
                    self.write(f.read())
                    self.finish()
                    
class UploadHandler(CASVerifiedRequestHandler):
    def post(self, action):
        if self.get_current_user() is None:
            self.validate_user()
            return
                
        if action == "template":
            print self.request.files[u'uploadedfiles[]'][0].keys()
            
            file_info = self.request.files[u'uploadedfiles[]'][0]
            
            import json
            
            data = {'file': file_info[u'filename'], 'type': file_info[u'content_type'], 'size': len(file_info[u'body'])}
            
            self.finish(json.dumps(data))

handlers = [
    (r'/(admin|logout|)', RequestHandler),
    (r'/upload/(.*)', UploadHandler),
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
