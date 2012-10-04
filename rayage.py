#!/usr/local/bin/python

import os
import json
import bottle
from bottle import route, static_file

system_directory = os.path.dirname(os.path.abspath(__file__))

bottle.debug(True)

@route('/')
def index():
    return static_file("index.html", root=system_directory, mimetype='text/html')
        
@route('/rayage.js')
def javascript():
    return static_file("rayage.js", root=system_directory, mimetype='text/javascript')
        
@route('/style.css')
def style():
    return static_file("style.css", root=system_directory, mimetype='text/css')
    
@route('/codemirror/<path:path>')
def codemirror(path):
    return static_file("/codemirror/" + path, root=system_directory)

@route('/images/<filename:re:.*\.png>')
def send_image(filename):
    return static_file(filename, root=system_directory+'/images', mimetype='image/png')

bottle.run(host='localhost', port=8080)
