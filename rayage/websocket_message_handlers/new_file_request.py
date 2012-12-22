from constants import *
import json
import os.path
from ..WebSocketHandler import messageHandler

@messageHandler("new_file_request", ["name", "filetype"])
def handle_new_file_request(socket_connection, message):
    """
    Handles new file requests - does not allow overwriting files.
    """
    filename = "%s%s" % (message['name'], message['filetype'])
    dst = socket_connection.project_dir(filename)

    if not dst:
        socket_connection.notify("You need a project open!", "error")
        return

    if os.path.exists(dst):
        socket_connection.notify("%s already exists!" % filename, "error")
        return

    # verify the file will end up in the user's directory
    if os.path.dirname(os.path.normpath(dst)) != os.path.normpath(socket_connection.project_dir()):
        socket_connection.notify("%s is an illegal filename!" % filename, "error")
        return

    file(dst, 'w').close()
    file("%s.swp" % dst, 'w').close()
    file("%s~" % dst, 'w').close()
    
    from .open_project_request import handle_open_project_request

    # reopen the project with newly created file.
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.log("debug","has created file \"{}\"".format(filename))
    socket_connection.notify("You just created %s!" % filename, "success")
