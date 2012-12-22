from constants import *
import os
import shutil
import json
from ..WebSocketHandler import messageHandler

@messageHandler("new_project_request", ["name", "template"])
def handle_new_project_request(socket_connection, message):
    """
    Handles new project requests by creating a directory in the user's projects folder.

    TODO:
    Send proper responses
    """
    
    name = message["name"]
    template = message["template"]
    if template == "": template_name = "empty template"
    else: template_name = template
    	
    try:
        new_project_dir = socket_connection.user_dir(name)

        # verify the project will end up in the user's directory
        if os.path.dirname(os.path.normpath(new_project_dir)) != os.path.normpath(socket_connection.user_dir()):
            socket_connection.notify("%s is an illegal project name!" % name, "error")
            return

        if template:
            shutil.copytree(os.path.join(TEMPLATES_DIR, template), new_project_dir)
        else:
            os.makedirs(new_project_dir)
            
        from .open_project_request import handle_open_project_request
            
        socket_connection.log("debug","Has created new project called \"{}\" from template \"{}\"".format(name,template_name))
        socket_connection.notify("You made a new project!", "success")
        handle_open_project_request(socket_connection, {'id': name}, False)
    except shutil.Error as e:
        # copytree error
        # This exception collects exceptions that are raised during a multi-file operation. 
        # For copytree(), the exception argument is a list of 3-tuples (srcname, dstname, exception).
        # TODO: Double check this. Existing project folder always falls into OSError.
        socket_connection.notify("Unknown project template.", "error")
    except OSError as e:
        # makedirs error
        socket_connection.notify("Project already exists.", "error")
