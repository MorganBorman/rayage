import json

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


@messageHandler("RayageJsonStore/Users")
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """
    print message
    
    result_message = {'type': message['type'],
                      'response': [{ 'id': 0, 'username': "bormanm", 'permissions': 'admin'}, { 'id': 1, 'username': "bjorgep", 'permissions': 'admin'}],
                      'deferredId': message['deferredId'],
                     }
                      
    socket_connection.write_message(json.dumps(result_message))

