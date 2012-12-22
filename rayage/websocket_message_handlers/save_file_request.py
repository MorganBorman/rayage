from constants import *
import json
import shutil
from ..WebSocketHandler import messageHandler

@messageHandler("save_file_request", ["filename"])
def handle_save_file_request(socket_connection, message):
    filename = message['filename']
    src = socket_connection.project_dir("%s.swp" % filename)
    dst = socket_connection.project_dir(filename)
    shutil.copyfile(src, dst)
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.notify("You just saved %s!" % filename, "success")
    socket_connection.log("debug","has saved file \"{}\"".format(filename))
