from constants import *
import json

from DojoQuery import DojoQuery
from DojoSort import DojoSort

from ..WebSocketHandler import messageHandler
from ..DojoWebsocketJsonStoreHandler import DojoWebsocketJsonStoreHandler

from ..database.User import User
from ..database.SessionFactory import SessionFactory

@messageHandler("WebsocketJsonStore/Users", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class UserStoreHandler(DojoWebsocketJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the users and their permissions.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        DojoWebsocketJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def object_to_json(self, user_object):
        return {'id': user_object.id, 'username': user_object.username, 'permissions': user_object.permission_level}
        
    def on_update(self, user_object):
        result_message = {'type': self.message_type,
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
            
            result_message = {'type': self.message_type,
                              'response': user_list,
                              'total': user_count,
                              'deferredId': message['deferredId'],
                             }
        finally:
            session.close()
        
        socket_connection.write_message(json.dumps(result_message))
        
    def delete(self, socket_connection, message, object_id):
        session = SessionFactory()
        try:
            assignment = session.query(User).filter(User.id==object_id).delete()
            session.commit()
        finally:
            session.close()
            
        self.on_delete(object_id)
        
    def put(self, socket_connection, message, object_data):
        target_id = object_data[u'id']
        target_username = object_data[u'username']
        target_permission_level = int(object_data[u'permissions'])
            
        if target_permission_level >= socket_connection.permission_level and not socket_connection.permission_level == PERMISSION_LEVEL_ADMIN:
            raise InsufficientPermissions("Cannot elevate user permissions higher than self.")
            
        session = SessionFactory()
        try:
            if target_id is not None:
                user = session.query(User).filter(User.id==int(target_id)).one()
                user.username = target_username
                user.permission_level = target_permission_level
            else:
                user = User(target_username, target_permission_level)
            
            session.add(user)
            session.commit()
            
            self.on_update(user)
        finally:
            session.close()
            
        result_message = {'type': self.message_type,
                          'response': self.object_to_json(user),
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
