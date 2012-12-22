from constants import *
import os
import json
import shutil
import os.path
from get_mime_type import get_mime_type

from ..WebSocketHandler import messageHandler

from ..database.User import User
from ..database.SessionFactory import SessionFactory

@messageHandler("open_project_request", ["id"])
def handle_open_project_request(socket_connection, message, notify=True, selected=""):
    """
    Handles open project requests by setting the project attribute of the users connection and sending a project state to the client.
    """
    project_id = message['id']
    
    if project_id != socket_connection.user.current_project:
        username = socket_connection.user.username
        
        session = SessionFactory()
        try:
            socket_connection.user.current_project = project_id
            session.add(socket_connection.user)
            session.commit()
        finally:
            session.close()
        #TODO: fix this hack! the attribute refresh operation does not succeed so
        #      a new instance of user has to be assigned to the socket connection
        socket_connection.user = User.get_user(username)
    
    project_dir = socket_connection.user_dir(project_id)

    if project_dir is None:
        return #TODO: generic error message

    if not os.path.isdir(project_dir):
        return #TODO: unknown project
        
    socket_connection.project = project_id
    
    def is_project_file(filename):
        root, ext = os.path.splitext(filename)
        return ext in PROJECT_DATA_EXTENSIONS
    
    project_files = filter(is_project_file, os.listdir(project_dir))
    
    project_file_data = []

    for filename in project_files:
        # create state files if they don't exist for some reason.
        if not os.path.exists(os.path.join(project_dir, "%s.swp" % filename)):
            dst = socket_connection.project_dir("%s.swp" % filename)
            src = socket_connection.project_dir(filename)
            shutil.copyfile(src, dst)
        if not os.path.exists(os.path.join(project_dir, "%s~" % filename)):
            open(os.path.join(project_dir, "%s~" % filename), 'w').close()

        with \
        open(os.path.join(project_dir, filename), "r") as file,\
        open(os.path.join(project_dir, "%s.swp" % filename), "r") as swap,\
        open(os.path.join(project_dir, "%s~" % filename), "r") as undo:
            f, s, u = (file.read(), swap.read(), undo.read())
            project_file_data.append({'filename': filename, 
                                      'mimetype': get_mime_type(os.path.join(project_dir, filename)),
                                      'data': s,
                                      'modified': f != s,
                                      'undo_data': json.loads(u or "null"),
                                      'selected': selected == filename})
    
    project_state = {'type': 'project_state',
                     'id': project_id,
                     'files': project_file_data}
    
    socket_connection.write_message(json.dumps(project_state))

    socket_connection.log("debug","has opened project \"{}\"".format(project_id))
    if notify:
        socket_connection.notify("You've opened %s!" % socket_connection.project, "success")
