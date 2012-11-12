import os
import json
import random
from sqlalchemy import func

from rayage_ws import messageHandler, MalformedMessage, InsufficientPermissions
from constants import *

from database.User import User
from database.SessionFactory import SessionFactory

from DojoQuery import DojoQuery
from DojoSort import DojoSort

admin_modules = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder', 'iconClass': 'modules'},
    { 'id': 'view_statistics', 'name': 'View Statistics', 'type': 'custom/StatisticsViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'view_statistics'},
    { 'id': 'user_manager', 'name': 'Manage Users', 'type': 'custom/UserManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'users'},
    { 'id': 'template_manager', 'name': 'Manage Templates', 'type': 'custom/TemplateManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'templates'},
]

@messageHandler("admin_module_tree_request", minimum_permission_level=PERMISSION_LEVEL_TA)
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """                                
    result_message = {'type': 'admin_module_tree',
                      'modules': admin_modules}
                      
    socket_connection.write_message(json.dumps(result_message))
    
    
class RayageJsonStoreHandler(object):
    def __init__(self):
        pass
        
    def __call__(self, socket_connection, message):
        action = message[u'action']
        
        if action == u'QUERY':
            options = {}
            if u'options' in message.keys():
                options = message[u'options']
            
            count = 30
            if u'count' in options.keys():
                count = int(options[u'count'])
                
            start = 0
            if u'start' in options.keys():
                start = int(options[u'start'])
                
            sort = None
            if u'sort' in options.keys():
                sort = options[u'sort']
                
            query = None
            if u'query' in options.keys():
                query = options[u'query']
                
            self.query(socket_connection, message, count, start, sort, query)
            
        elif action == u'PUT':
            object_data = json.loads(message[u'objectData'])
            
            self.put(socket_connection, message, object_data)
            
        else:
            raise Exception("Unsupported RayageJsonStore action: {}".format(action))
            
    def query(self, socket_connection, message, count, start, sort, query):
        raise Exception("Not implemented RayageJsonStore action: {}".format(message[u'action']))
        
    def put(self, socket_connection, message, object_data):
        raise Exception("Not implemented RayageJsonStore action: {}".format(message[u'action']))
        
@messageHandler("RayageJsonStore/Users", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class UserStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the users and their permissions.
    """
    def __init__(self):
        RayageJsonStoreHandler.__init__(self)
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(User.id, User.username, User.permission_level)
        
            column_map = {u'id': User.id, u'username': User.username, u'permissions': User.permission_level}
        
            if dojo_query is not None:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            user_count = query.count()
            user_list = query.offset(start).limit(count).all()
            user_list = [{'id': uid, 'username': username, 'permissions': permission_level} for uid, username, permission_level in user_list]
            
            result_message = {'type': message[u'type'],
                              'response': user_list,
                              'total': user_count,
                              'deferredId': message['deferredId'],
                             }
        finally:
            session.close()
        
        socket_connection.write_message(json.dumps(result_message))
        
    def put(self, socket_connection, message, object_data):
            
        target_permission_level = int(object_data[u'permissions'])
            
        session = SessionFactory()
        try:
            if target_permission_level >= socket_connection.permission_level and not socket_connection.permission_level == PERMISSION_LEVEL_ADMIN:
                raise InsufficientPermissions("Cannot elevate user permissions higher than self.")
            
            user = User.get_user(object_data[u'username'])
            user.permission_level = target_permission_level
            
            session.add(user)
            session.commit()
        finally:
            session.close()
            
        result_message = {'type': message[u'type'],
                          'response': [],
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
        
@messageHandler("RayageJsonStore/Templates", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class TemplateStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the templates.
    """
    def __init__(self):
        RayageJsonStoreHandler.__init__(self)
        
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
    
