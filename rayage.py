#!/usr/local/bin/python

import os
import sys
import json
import socket

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.websocket
import tornado.web
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.template

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    authenticated = False

    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        msg = json.loads(message)
        print msg
        self.write_message(message)

    def on_close(self):
        print "WebSocket closed"

handlers = [
    (r'/()', tornado.web.StaticFileHandler, {'path': system_directory+'/static', 'default_filename': 'index.html'}),
    (r'/(rayage\.js|welcome\.html)', tornado.web.StaticFileHandler, {'path': system_directory+'/static'}),
    (r'/codemirror/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/codemirror'}),
    (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/images'}),
    (r'/styles/(.*)', tornado.web.StaticFileHandler, {'path': system_directory+'/static/styles'}),
    (r'/ws', WebSocketHandler),
]

if __name__ == "__main__":
        tornado_app = tornado.web.Application(handlers)
        
        tornado_http = tornado.httpserver.HTTPServer(tornado_app, ssl_options= {"certfile": "misc/server.crt", "keyfile": "misc/server.key"})
        tornado_http.bind(8080, family=socket.AF_INET)
        tornado_http.start()
        tornado.ioloop.IOLoop.instance().start()
