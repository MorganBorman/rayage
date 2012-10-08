import tornado.websocket
import json

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
    def __init__(self, message_type, required_fields, require_auth=True):
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
        
@messageHandler("login_request", ["username", "password"], False)
def handle_login_request(socket_connection, message):
    if message['username'] == "test" and message['password'] == "password":
        socket_connection.authenticated = True
        result_message = {'type': 'login_success'}
    else:
        result_message = {'type': 'login_failure'}
        
    socket_connection.write_message(json.dumps(result_message))





