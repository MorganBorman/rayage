from constants import *
import json

import os.path

from ..WebSocketHandler import messageHandler
from ..DojoWebsocketJsonStoreHandler import DojoWebsocketJsonStoreHandler

@messageHandler("WebsocketJsonStore/Templates", ['action', 'deferredId'])
class TemplateStoreHandler(DojoWebsocketJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the templates.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        DojoWebsocketJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def on_change(self, pathname, action):
        t = os.path.basename(pathname)
        
        result_message = {'type': "WebsocketJsonStore/Templates",
                          'action': action,
                          'object': {'id': t, 'label': t},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
    
        template_list = [{'id': t, 'label': t} for t in os.listdir(TEMPLATES_DIR) 
                                           if os.path.isdir(os.path.join(TEMPLATES_DIR, t))]
            
        template_count = len(template_list)
            
        result_message = {'type': message[u'type'],
                          'response': template_list,
                          'total': template_count,
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
        
    def get(self, socket_connection, message, object_id):
        result_message = {'type': message[u'type'],
                          'response': {u'id': object_id, u'label': object_id},
                          'deferredId': message['deferredId'],
                         }
                         
        socket_connection.write_message(json.dumps(result_message))
