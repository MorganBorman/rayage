import database

from WebSocketHandler import WebSocketHandler
from UploadHandler import UploadHandler
from DownloadHandler import DownloadHandler
from PageRequestHandler import PageRequestHandler
#from FakeUserRequestHandler import FakeUserRequestHandler

import rayage.websocket_message_handlers
import rayage.upload_handlers
import rayage.download_handlers

handlers = [
    (r'/(admin|logout|)', PageRequestHandler),
    (r'/upload/(.*)', UploadHandler),
    (r'/download/(.*)/(.*)', DownloadHandler),
    (r'/ws', WebSocketHandler),
    #(r'/fake_user/(.*)', FakeUserRequestHandler),
]
