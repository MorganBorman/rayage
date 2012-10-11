#!/usr/local/bin/python

import os
import sys
import socket

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.web
import tornado.httpserver
import tornado.ioloop

from rayage_ws import WebSocketHandler

handlers = [
    (r'/()', tornado.web.StaticFileHandler, {'path': system_directory+'/static', 'default_filename': 'index.html'}),
    (r'/(.*\.js|welcome\.html)', tornado.web.StaticFileHandler, {'path': system_directory+'/static'}),
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
