from constants import *
import json
import time
import shutil
import os.path
from ..WebSocketHandler import messageHandler

@messageHandler("delete_file_request", ["file"])
def handle_delete_file_request(socket_connection, message):
    f = message["file"]
    src = socket_connection.project_dir(f)
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.move(src, dst)
    shutil.move(src+".swp", dst)
    shutil.move(src+"~", dst)
    
    from .open_project_request import handle_open_project_request
    
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just deleted %s." % f, "success")
    socket_connection.log("debug","has deleted file \"{}\"".format(f))
