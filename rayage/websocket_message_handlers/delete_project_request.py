from constants import *
import json
import os.path
import shutil
import time
from ..WebSocketHandler import messageHandler

@messageHandler("delete_project_request", [])
def handle_delete_project_request(socket_connection, message):
    src = socket_connection.project_dir()
    # move to trash
    # trash/username/projectname/timestamp/
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    shutil.move(src, dst)
    # notify on deletion and close their windows
    socket_connection.notify("You just deleted %s." % socket_connection.project, "success")
    socket_connection.log("debug","has deleted project \"{}\"".format(socket_connection.project))
    
    from .close_project_request import handle_close_project_request
    handle_close_project_request(socket_connection, {}, False)
