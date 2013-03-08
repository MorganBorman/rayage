#!/usr/local/bin/python

import os
import sys
import socket

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import constants

from rayage.logger import logger
from rayage import handlers

import tornado.options
import tornado.web
import tornado.httpserver
import tornado.ioloop

if __name__ == "__main__":
    tornado_app = tornado.web.Application(handlers,
                                          debug=constants.DEBUG,
                                          cookie_secret=constants.COOKIE_SECRET, 
                                          template_path=system_directory+"/templates", 
                                          static_path=system_directory+"/static",
                                          gzip=True)
    
    tornado.options.parse_command_line()
    
    tornado_http = tornado.httpserver.HTTPServer(tornado_app, ssl_options= {"certfile": "misc/server.crt", "keyfile": "misc/server.key"})
    tornado_http.bind(8080, family=socket.AF_INET)
    tornado_http.start()
    logger.info("Rayage started.")
    
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "\nReceived KeyboardInterrupt exiting..."
