from constants import *
import json
from ..WebSocketHandler import messageHandler

@messageHandler("project_state_push", ["files"])
def handle_project_state_push(socket_connection, message):
    if socket_connection.project is None:
        socket_connection.notify("There's been a catastrophic failure. Please manually save any data to your local machine (copy/paste) and refresh.", "error")
        return

    for file in message['files']:
        socket_connection.log("debug","has pushed state for file \"{}\"".format(file['filename']))
        # if modified, overwrite the .swp file with new data
        if file['modified']:
            with open(socket_connection.project_dir("%s.swp" % file['filename']), 'w+') as f:
                f.write(file['data'])

        # overwrite the undo history - stored as JSON in FILENAME.cpp~
        with open(socket_connection.project_dir("%s~" % file['filename']), 'w+') as f:
            f.write(json.dumps(file['undo_data']))
