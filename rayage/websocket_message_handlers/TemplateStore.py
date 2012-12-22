from constants import *
import json

import os.path

from ..WebSocketHandler import messageHandler
from ..RayageJsonStoreHandler import RayageJsonStoreHandler

@messageHandler("RayageJsonStore/Templates", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class TemplateStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the templates.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        RayageJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def on_change(self, pathname, action):
        t = os.path.basename(pathname)
        
        result_message = {'type': "RayageJsonStore/Templates",
                          'action': action,
                          'object': {'id': t, 'name': t},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
    
        template_list = [{'id': t, 'name': t} for t in os.listdir(TEMPLATES_DIR) 
                                           if os.path.isdir(os.path.join(TEMPLATES_DIR, t))]
            
        template_count = len(template_list)
            
        result_message = {'type': message[u'type'],
                          'response': template_list,
                          'total': template_count,
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
