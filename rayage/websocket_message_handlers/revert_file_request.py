from constants import *
import json
import time
import shutil
from ..WebSocketHandler import messageHandler

@messageHandler("revert_file_request", ["filename"])
def handle_open_file_request(socket_connection, message):
    filename = message['filename']
    dst = socket_connection.project_dir("%s.swp" % filename)
    src = socket_connection.project_dir(filename)
    shutil.copyfile(src, dst)
    
    from .open_project_request import handle_open_project_request
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.notify("You just reverted %s!" % filename, "success")
    socket_connection.log("debug","has reverted file \"{}\"".format(filename))
