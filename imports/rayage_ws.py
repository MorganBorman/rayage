import tornado.websocket
import tornado.web

import json
import os
import shutil

from database.User import User
from constants import *
from ws_exceptions import InsufficientPermissions, InvalidStateError, MalformedMessage

from logger import logger

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    message_handlers = {}
    
    active_users = {} # key: username, value: list of websocket connections
    
    streams = {} # key: stream name, value: minimum permission level
    subscribers = {} # key: stream name, value: list of websocket connections

    user = None
    authenticated = False
    project = None
    project_runner = None
    subscriptions = [] # holds a list stream names
    
    def log(self, level, message):
        ip = self.request.remote_ip
        logger.__getattribute__(level)("{}@{}: {}".format(self.username, ip, message))
    
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
        return PERMISSION_LEVEL_NONE
        
    @staticmethod
    def write_message_username(username, message_data):
        if username in WebSocketHandler.active_users.keys():
            for socket_connection in WebSocketHandler.active_users[username]:
                socket_connection.write_message(message_data)
                
    @staticmethod
    def notify_username(username, msg, severity="message", duration=1.5):
        if username in WebSocketHandler.active_users.keys():
            for socket_connection in WebSocketHandler.active_users[username]:
                socket_connection.notify(msg, severity, duration)
        
    @staticmethod
    def register_stream(stream_name, minimum_permission_level=PERMISSION_LEVEL_USER):
        WebSocketHandler.streams[stream_name] = minimum_permission_level
        
    @staticmethod
    def publish(stream_name, message_data):
        if stream_name in WebSocketHandler.subscribers.keys():
            for socket_connection in WebSocketHandler.subscribers[stream_name]:
                socket_connection.write_message(message_data)
        
    def subscribe(self, stream_name):
        if not stream_name in WebSocketHandler.streams.keys():
            raise InvalidStateError("Unknown stream.")
            
        if self.permission_level < WebSocketHandler.streams[stream_name]:
            raise InsufficientPermissions()
        
        self.subscriptions.append(stream_name)
        
        if not stream_name in WebSocketHandler.subscribers.keys():
            WebSocketHandler.subscribers[stream_name] = []
        
        WebSocketHandler.subscribers[stream_name].append(self)
        
    def unsubscribe(self, stream_name):
        if stream_name in self.subscriptions:
            self.subscriptions.remove(stream_name)
            
        if stream_name in WebSocketHandler.subscribers.keys():
            if self in WebSocketHandler.subscribers[stream_name]:
                WebSocketHandler.subscribers[stream_name].remove(self)
    
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
        self.subscriptions = []
        
        username = self.get_secure_cookie("user")
        
        if username is not None:
            self.user = User.get_user(username)
            
            if self.user is not None:
                # Check if "new" user and create a project dir for them if needed.
                if not os.path.exists(self.user_dir()):
                    os.makedirs(self.user_dir())
                
                if not self.username in self.active_users.keys():
                    self.active_users[self.username] = []
                self.active_users[self.username].append(self)
                
                self.user.on_connect()
                
                result_message = {'type': 'login_success'}
                self.write_message(json.dumps(result_message))
                
                if self.user.current_project is not None:
                    # Send a message to re-open the current project
                    #TODO: fix this hack! this module should not "know" about this method.
                    self.message_handlers["open_project_request"](self, {'id': self.user.current_project})
                
                self.log("info", "User '{}' has connected.".format(self.username))
                return

        self.redirect(CAS_SERVER + "/cas/login?service=" + SERVICE_URL, permanent=False)
        
        self.notify("Session expired. Please login again.", "error")
        
    def access_denied(self, details):
        message = "Access denied. {}".format(details)
        self.log("error", message)
        self.notify(message, "error")
        
    def malformed_message(self, details):
        message = "Invalid message. {}".format(details)
        self.log("error", message)
        self.notify(message, "error")

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
            self.log("info", "User '{}' has disconnected.".format(self.username))
            
        if self.user is not None:
            self.user.on_disconnect()
            
        if self.username in self.active_users.keys():
            if self in self.active_users[self.username]:
                self.active_users[self.username].remove(self)
            
        if len(self.subscriptions) > 0:
            for stream_name in self.subscriptions[:]:
                self.unsubscribe(stream_name)

class messageHandler(object):
    def __init__(self, message_type, required_fields=[], minimum_permission_level=PERMISSION_LEVEL_USER):
        self.message_type = message_type
        self.required_fields = required_fields
        self.minimum_permission_level = minimum_permission_level

    def __call__(self, f):
        if type(f) == type:
            f = f(self.message_type, self.required_fields, self.minimum_permission_level)
        
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
        
class StreamHandle(object):
    def __init__(self, stream_name, minimum_permission_level=PERMISSION_LEVEL_USER):
        self.stream_name = stream_name
        
        WebSocketHandler.register_stream(stream_name, minimum_permission_level)
        
    def publish(self, message_data):
        WebSocketHandler.publish(self.stream_name, message_data)
        
@messageHandler("subscribe_request", ['stream'])
def handle_admin_module_tree_request(socket_connection, message):
    """
    Subscribes this websocket connection to a message stream.
    """
    socket_connection.subscribe(message['stream'])
    
    result_message = {'type': 'subscribe_ack',
                      'stream': message['stream']}
                      
    socket_connection.write_message(json.dumps(result_message))
