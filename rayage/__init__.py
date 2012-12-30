import database

from WebSocketHandler import WebSocketHandler
from UploadHandler import UploadHandler
from PageRequestHandler import PageRequestHandler
#from FakeUserRequestHandler import FakeUserRequestHandler

import rayage.websocket_message_handlers
import rayage.upload_handlers

handlers = [
    (r'/(admin|logout|)', PageRequestHandler),
    (r'/upload/(.*)', UploadHandler),
    (r'/ws', WebSocketHandler),
    #(r'/fake_user/(.*)', FakeUserRequestHandler),
]
