import tornado.websocket
import json
import hashlib
import hmac
import time
import os
import errno
import shutil
from constants import *

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
            return
    result_message = {'type': 'login_failure'}
    socket_connection.write_message(json.dumps(result_message))
    
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
    else:
        result_message = {'type': 'login_failure'}
        
    socket_connection.write_message(json.dumps(result_message))

@messageHandler("logout_request")
def handle_logout_request(socket_connection, message):
    # Need to use the stored (should be stored) username to clear any current sessions for that user
    result_message = {'type': 'logout_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))

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
        # TODO: Acknowledge success
        socket_connection.write_message(json.dumps("TODO: Successful New Project"))
    except shutil.Error as e:
        # copytree error
        # This exception collects exceptions that are raised during a multi-file operation. 
        # For copytree(), the exception argument is a list of 3-tuples (srcname, dstname, exception).
        # TODO: Double check this. Existing project folder always falls into OSError.
        socket_connection.write_message(json.dumps("TODO: Missing template"))
    except OSError as e:
        # makedirs error
        socket_connection.write_message(json.dumps("TODO: Existing Project" + str(e)))

