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
    project_runner = None
    
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
        
    def access_denied(self, details):
        self.notify("Access denied. {}".format(details), "error")
        
    def malformed_message(self, details):
        self.notify("Invalid message. {}".format(details), "error")

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
            self.access_denied(e.message)
            
        except MalformedMessage, e:
            self.malformed_message(e.message)

    def on_close(self):
        if self.username is not None:
            print "User '{}' has disconnected.".format(self.username)

class messageHandler(object):
    def __init__(self, message_type, required_fields=[], minimum_permission_level=PERMISSION_LEVEL_USER):
        self.message_type = message_type
        self.required_fields = required_fields
        self.minimum_permission_level = minimum_permission_level

    def __call__(self, f):
        if type(f) == type:
            f = f()
        
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
