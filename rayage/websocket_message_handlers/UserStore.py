from constants import *
import json

from DojoQuery import DojoQuery
from DojoSort import DojoSort

from ..WebSocketHandler import messageHandler
from ..RayageJsonStoreHandler import RayageJsonStoreHandler

from ..database.User import User
from ..database.SessionFactory import SessionFactory

@messageHandler("RayageJsonStore/Users", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class UserStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the users and their permissions.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        RayageJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def on_update(self, user_object):
        result_message = {'type': "RayageJsonStore/Users",
                          'action': 'update',
                          'object': {'id': user_object.id, 'username': user_object.username, 'permissions': user_object.permission_level},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(User.id, User.username, User.permission_level, User.user_since, User.last_online)
        
            column_map = {u'id': User.id, u'username': User.username, u'permissions': User.permission_level}
        
            if dojo_query:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            user_count = query.count()
            user_list = query.offset(start).limit(count).all()
            user_list = [{'id': uid, 'username': username, 'permissions': permission_level, 'user_since': user_since, 'last_online': last_online} for uid, username, permission_level, user_since, last_online in user_list]
            
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
            
            self.on_update(user)
            
            session.add(user)
            session.commit()
        finally:
            session.close()
            
        result_message = {'type': message[u'type'],
                          'response': [],
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
