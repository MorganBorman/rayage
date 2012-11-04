import json
import random

from rayage_ws import messageHandler

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

from names import names
            
user_table = []

i = 0
for name in names:
    user_table.append({'id': i, 'username': name, 'permissions': random.randrange(0,3)})
    i += 1

@messageHandler("RayageJsonStore/Users")
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """
    print message
    
    options = {}
    if u'options' in message.keys():
        options = message[u'options']
    
    count = 1000
    if u'count' in options.keys():
        print "foo"
        count = int(options[u'count'])
        
    start = 0
    if u'start' in options.keys():
        print "bar"
        start = int(options[u'start'])
        
    end_index = min(start+count, len(user_table))
    
    print start, end_index
    
    result_message = {'type': message[u'type'],
                      'response': user_table[start:end_index],
                      'total': len(user_table),
                      'deferredId': message['deferredId'],
                     }
    
    socket_connection.write_message(json.dumps(result_message))

