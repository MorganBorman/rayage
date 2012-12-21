import database

from WebSocketHandler import WebSocketHandler
from UploadHandler import UploadHandler
from PageRequestHandler import PageRequestHandler
#from FakeUserRequestHandler import FakeUserRequestHandler

import editor_handlers
import admin_handlers

handlers = [
    (r'/(admin|logout|)', PageRequestHandler),
    (r'/upload/(.*)', UploadHandler),
    (r'/ws', WebSocketHandler),
    #(r'/fake_user/(.*)', FakeUserRequestHandler),
]
