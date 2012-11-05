import json
import random
from sqlalchemy import func

from rayage_ws import messageHandler

from database.User import User
from database.SessionFactory import SessionFactory

from DojoQuery import DojoQuery

admin_modules = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder', 'iconClass': 'modules'},
    { 'id': 'view_statistics', 'name': 'View Statistics', 'type': 'custom/StatisticsViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'view_statistics'},
    { 'id': 'user_manager', 'name': 'Manage Users', 'type': 'custom/UserManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'users'},
    { 'id': 'template_manager', 'name': 'Manage Templates', 'type': 'custom/TemplateManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'templates'},
]

@messageHandler("admin_module_tree_request")
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """                                
    result_message = {'type': 'admin_module_tree',
                      'modules': admin_modules}
                      
    socket_connection.write_message(json.dumps(result_message))

@messageHandler("RayageJsonStore/Users")
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """
    print message
    
    options = {}
    if u'options' in message.keys():
        options = message[u'options']
    
    count = 30
    if u'count' in options.keys():
        count = int(options[u'count'])
        
    start = 0
    if u'start' in options.keys():
        start = int(options[u'start'])
        
    dojo_query = None
    if u'query' in options.keys():
        dojo_query = options[u'query']
    
    session = SessionFactory()
    try:
        query = session.query(User.id, User.username, User.permission_level)
    
        if dojo_query is not None:
            column_map = {u'id': User.id, u'username': User.username, u'permissions': User.permission_level}
            
            dojo_query_obj = DojoQuery(dojo_query)
            query = dojo_query_obj.apply_to_sqla_query(query, column_map)
        
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

