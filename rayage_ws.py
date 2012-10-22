import tornado.websocket
import tornado.web

import json
import os
import shutil

from database.User import User
from constants import *

class MalformedMessage(Exception):
    '''A message is missing fields or fields are invalid.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)
        
class InsufficientPermissions(Exception):
    '''A message is issued without sufficient permissions.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    message_handlers = {}

    user = None
    authenticated = False
    project = None
    
    @property
    def username(self):
        """
        Returns the username associated with this connection.
        """
        if self.user is not None:
            return self.user.username
        return None
        
    @property
    def permission_level(self):
        """
        Returns the permission_level associated with this connection.
        """
        if self.user is not None:
            return self.user.permission_level
        return 0
    
    def user_dir(self, *args):
        """
        Returns paths within current user's projects folder.
        """
        if self.username is None:
            return None
        
        if len(args) < 1:
            return os.path.join(STUDENTS_DIR, self.username)
            
        return os.path.join(STUDENTS_DIR, self.username, os.path.join(*args))

    def project_dir(self, *args):
        "Returns paths within the current user's current project directory (or None if no project or user)."
        if self.project is None:
            return None

        return self.user_dir( *((self.project,) + args) )

    def notify(self, msg, severity="message", duration=1.5):
        """
        Displays a non-blocking message to the user with a duration in seconds
        and one of the following severities: ["fatal", "error", "warning", "message"]
        """
        severities = ["notice", "info", "success", "error"]
        if severity not in severities:
            severity = "notice"

        notification = {'type': 'notification',
                         'message': msg,
                         'duration': duration*1000,
                         'severity': severity}
        self.write_message(json.dumps(notification))
        
    def redirect(self, target, permanent):
        redirection = {'type': 'redirect',
                         'target': target}
        self.write_message(json.dumps(redirection))

    def open(self):
        username = self.get_secure_cookie("user")
        
        if username is not None:
            self.user = User.get_user(username)

            # Check if "new" user and create a project dir for them if needed.
            if not os.path.exists(self.user_dir()):
                os.makedirs(self.user_dir())

            result_message = {'type': 'login_success'}
            self.write_message(json.dumps(result_message))
            
            print "User '{}' has connected.".format(self.username)
        else:
            self.redirect(CAS_SERVER + "/cas/login?service=" + SERVICE_URL, permanent=False)
            
            self.notify("Session expired. Please login again.", "error")
        
    def access_denied(self):
        self.notify("Access denied.", "error")
        
    def malformed_message(self):
        self.notify("Invalid message.", "error")

    def on_message(self, message):
        try:
            msg = json.loads(message)
            
            if not "type" in msg.keys():
                raise MalformedMessage()
            
            msgtype = msg["type"]
            
            if not msgtype in self.message_handlers.keys():
                raise MalformedMessage()
                
            self.message_handlers[msgtype](self, msg)

        except InsufficientPermissions, e:
            self.access_denied()
            
        except MalformedMessage, e:
            self.malformed_message()

    def on_close(self):
        if self.username is not None:
            print "User '{}' has disconnected.".format(self.username)

class messageHandler(object):
    def __init__(self, message_type, required_fields=[], minimum_permission_level=1):
        self.message_type = message_type
        self.required_fields = required_fields
        self.minimum_permission_level = minimum_permission_level

    def __call__(self, f):
        def handler(socket_connection, message):
            for field in self.required_fields:
                if not field in message.keys():
                    raise MalformedMessage()
                    
            if self.minimum_permission_level > socket_connection.permission_level:
                raise InsufficientPermissions()
                
            f(socket_connection, message)
        
        self.handler = handler
        
        WebSocketHandler.message_handlers[self.message_type] = handler
        
        return f

<<<<<<< HEAD
@messageHandler("project_list_request")
def handle_project_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available projects to work on to our socket.
    Currently a flat list of folders in the STUDENTS_DIR
    """
    projects = [{'label': p, 'id': p} for p in os.listdir(socket_connection.user_dir()) 
                                      if os.path.isdir(socket_connection.user_dir(p))]
                                      
    result_message = {'type': 'project_list',
                      'projects': projects}
    socket_connection.write_message(json.dumps(result_message))
    
@messageHandler("close_project_request")
def handle_close_project_list(socket_connection, message, notify=True):
    """
    Sets the current project for the given socket_connection to None and returns an
    acknowledgement that the project has been closed.
    """
    socket_connection.project = None
    result_message = {'type': 'close_project_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))
    if notify:
        socket_connection.notify("You've closed your project!", "success")

@messageHandler("template_list_request")
def handle_template_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available templates to our socket.
    Currently a flat list of folders in the TEMPLATES_DIR

    TODO:
    Use a "real" id of some sort (at least remove problematic chars)

    """
    templates = [{'label': t, 'id': t} for t in os.listdir(TEMPLATES_DIR) 
                                       if os.path.isdir(os.path.join(TEMPLATES_DIR, t))]
    templates.insert(0, {'label': 'Empty Template', 'id': ''})

    result_message = {'type': 'template_list', 
                      'templates': templates}
    socket_connection.write_message(json.dumps(result_message))
    
@messageHandler("file_type_list_request")
def handle_file_type_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available file types which may be created to our socket.
    """                
    types = [{'label': t, 'id': t} for t in PROJECT_DATA_EXTENSIONS]
         
    result_message = {'type': 'file_type_list',
                      'types': types}
                      
    socket_connection.write_message(json.dumps(result_message))

@messageHandler("new_project_request", ["name", "template"], True)
def handle_new_project_request(socket_connection, message):
    """
    Handles new project requests by creating a directory in the user's projects folder.

    TODO:
    Send proper responses
    """
    name = message["name"]
    template = message["template"]

    try:
        new_project_dir = socket_connection.user_dir(name)
        if template:
            shutil.copytree(os.path.join(TEMPLATES_DIR, template), new_project_dir)
        else:
            os.makedirs(new_project_dir)

        socket_connection.notify("You made a new project!", "success")
        handle_open_project_request(socket_connection, {'id': name})
    except shutil.Error as e:
        # copytree error
        # This exception collects exceptions that are raised during a multi-file operation. 
        # For copytree(), the exception argument is a list of 3-tuples (srcname, dstname, exception).
        # TODO: Double check this. Existing project folder always falls into OSError.
        socket_connection.notify("Unknown project template.", "error")
    except OSError as e:
        # makedirs error
        socket_connection.notify("Project already exists.", "error")

@messageHandler("open_project_request", ["id"], True)
def handle_open_project_request(socket_connection, message, notify=True):
    """
    Handles open project requests by setting the project attribute of the users connection and sending a project state to the client.
    """
    project_id = message['id']
    
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
        with open(os.path.join(project_dir, filename), "r") as f:
            project_file_data.append({'filename': filename, 
                                      'mimetype': get_mime_type(os.path.join(project_dir, filename)),
                                      'data': f.read(), 
                                      'modified': False, 
                                      'undo_data': None})
    
    project_state = {'type': 'project_state',
                     'id': project_id,
                     'files': project_file_data}
    
    socket_connection.write_message(json.dumps(project_state))
    socket_connection.notify("You've opened %s!" % socket_connection.project, "success")

@messageHandler("new_file_request", ["name", "filetype"], True)
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

    file(dst, 'w').close()
    # reopen the project with newly created file.
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just created %s!" % filename, "success")

@messageHandler("delete_project_request", [], True)
def handle_delete_project_request(socket_connection, message):
    src = socket_connection.project_dir()
    # move to trash
    # trash/username/projectname/timestamp/
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    shutil.move(src, dst)
    # notify on deletion and close their windows
    socket_connection.notify("You just deleted %s." % socket_connection.project, "success")
    handle_close_project_list(socket_connection, {}, False)
=======

>>>>>>> b59d9a1f16e4d8f07a81ca56a17ba46e444a2e0d
