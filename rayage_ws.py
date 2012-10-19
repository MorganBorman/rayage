import tornado.websocket
import json
import hashlib
import hmac
import time
import os
import errno
import shutil
from constants import *

import mimetypes
mimetypes.init()

def get_mime_type(full_filename):
    "Returns the mimetype for a file given its fully qualified filename."
    mime, encoding = mimetypes.guess_type(full_filename)
    return mime

try:
    import Crypto.Random
    import Crypto.Util.number
    def get_random_bytes(b):
        return Crypto.Util.number.getRandomNBitInteger(b*8, Crypto.Random.get_random_bytes)
except ImportError:
    import random
    print("Warning using non-cryptographically random session keys. Please install pycrypto.")
    def get_random_bytes(b):
        return random.getrandbits(b*8)

def sign_cookie(signing_key, value):
    hm = hmac.new(signing_key, value, hashlib.sha256)
    return hm.hexdigest()
    
def check_cookie(signing_key, full_cookie_value):
    cookie_value, cookie_signature = full_cookie_value.rsplit("&", 1)
    return sign_cookie(signing_key, cookie_value)

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

    authenticated = False
    _username = None
    _project = None
    
    @property
    def username(self):
        "Gets the currently authenticated username for this connection."
        if not self.authenticated:
            return None
        return self._username
        
    @username.setter
    def username(self, value):
        "Sets the currently authenticated username for this connection."
        self._username = value
    
    def user_dir(self, *args):
        """
        Returns paths within current user's projects folder.
        """
        if self.username is None:
            return None
        
        if len(args) < 1:
            return os.path.join(STUDENTS_DIR, self.username)
            
        return os.path.join(STUDENTS_DIR, self.username, os.path.join(*args))
        
    @property
    def project(self):
        "Gets the current project for the currently authenticated user."
        if self.username is None:
            return None
            
        return self._project
        
    @project.setter
    def project(self, value):
        "Sets the current project for the currently authenticated user."
        self._project = value

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

    def open(self):
        print "WebSocket opened"
        
    def access_denied(self):
        self.write_message(json.dumps({"type": "access_denied", "reason": "not authenticated"}))
        
    def malformed_message(self):
        self.write_message(json.dumps({"type": "error", "detail": "invalid message"}))

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
        print "WebSocket closed"

class messageHandler(object):
    def __init__(self, message_type, required_fields=[], require_auth=True):
        self.message_type = message_type
        self.required_fields = required_fields
        self.require_auth = require_auth

    def __call__(self, f):
        def handler(socket_connection, message):
            for field in self.required_fields:
                if not field in message.keys():
                    raise MalformedMessage()
                    
            if self.require_auth and not socket_connection.authenticated:
                raise InsufficientPermissions()
                
            f(socket_connection, message)
        
        self.handler = handler
        
        WebSocketHandler.message_handlers[self.message_type] = handler
        
        return f
    

secret_key = "foobarbaz" # A (hopefully) long string used to sign the session key cookie to prevent tampering

users = {"test": hashlib.sha256("password").hexdigest()}

session_timeout = 600

# In the future these would need to be stored as seperate components rather than just the session cookie string
# ... and in a DB obviously
sessions = {}

def generate_session_cookie(secret_key, username, expiry_length):
    # Example of how signing of the session keys could work
    
    # A random key used to identify a client session across seperate websocket connections without re-verifying their password
    session_key = format(get_random_bytes(16), 'X')
    
    # Store this in the database with the user credentials. Later when the client sends the cookie back we see whether it matches
    cookie_value = "username=%s&expires=%d&key=%s" %(username, int(time.time()) + expiry_length, session_key)
    
    # This is the value we send to the client for them to store in a cookie
    return cookie_value + "&" + sign_cookie(secret_key, cookie_value)

@messageHandler("continue_session", ["cookie_value"], False)
def handle_continue_session(socket_connection, message):
    cookie_value = message['cookie_value']
    
    # use this to theck the validity of the cookie when the client sends it back later. 
    # This in combination with verifying the session key against the database and checking whether it has expired should ensure that only valid sessions can be resumed.
    if check_cookie(secret_key, cookie_value):
        username = cookie_value.split("&", 1)[0].split("=", 1)[1]
        if username in sessions.keys() and sessions[username] == cookie_value:
            socket_connection.authenticated = True
            socket_connection.username = username
            session_cookie = generate_session_cookie(secret_key, username, session_timeout)
            sessions[username] = session_cookie
            result_message = {'type': 'login_success', 'session_cookie': session_cookie, 'session_timeout': int(time.time())+session_timeout}
            socket_connection.write_message(json.dumps(result_message))
            socket_connection.notify("Welcome back!", "success")
            return
    socket_connection.notify("Please login.", "error")
    
@messageHandler("login_request", ["username", "password"], False)
def handle_login_request(socket_connection, message):
    username = message['username']
    password = message['password']
    
    if username in users.keys() and password == users[username]:
        socket_connection.authenticated = True
        socket_connection.username = username
        session_cookie = generate_session_cookie(secret_key, username, session_timeout)
        sessions[username] = session_cookie
        result_message = {'type': 'login_success', 'session_cookie': session_cookie, 'session_timeout': int(time.time())+session_timeout}
        socket_connection.write_message(json.dumps(result_message))
        socket_connection.notify("Now logged in.", "success")
    else:
        socket_connection.notify("Incorrect username or password. Please try again.", "error")

@messageHandler("logout_request")
def handle_logout_request(socket_connection, message):
    """
    Handles logout requests.
    """
    socket_connection.authenticated = False
    # Need to use the stored (should be stored) username to clear any current sessions for that user
    result_message = {'type': 'logout_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))
    socket_connection.notify("You've logged out!", "success")

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
def handle_close_project_list(socket_connection, message):
    """
    Sets the current project for the given socket_connection to None and returns an
    acknowledgement that the project has been closed.
    """
    socket_connection.project = None
    result_message = {'type': 'close_project_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))
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

    if os.path.exists(dst):
        socket_connection.notify("%s already exists!" % filename, "error")
        return

    file(dst, 'w').close()
    # reopen the project with newly created file.
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just created %s!" % filename, "success")