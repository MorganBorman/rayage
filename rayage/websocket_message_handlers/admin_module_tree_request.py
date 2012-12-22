from constants import *
import json
from ..WebSocketHandler import messageHandler

admin_modules = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder', 'iconClass': 'modules'},
    { 'id': 'view_statistics', 'name': 'View Statistics', 'type': 'custom/StatisticsViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'view_statistics'},
    { 'id': 'user_manager', 'name': 'Manage Users', 'type': 'custom/UserManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'users'},
    { 'id': 'template_manager', 'name': 'Manage Templates', 'type': 'custom/TemplateManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'templates'},
    { 'id': 'assignment_manager', 'name': 'Manage Assignments', 'type': 'custom/AssignmentManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'assignments'},
    { 'id': 'log_viewer', 'name': 'View Logs', 'type': 'custom/LogViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'logs'},
]

@messageHandler("admin_module_tree_request", minimum_permission_level=PERMISSION_LEVEL_TA)
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """                                
    result_message = {'type': 'admin_module_tree',
                      'modules': admin_modules}
                      
    socket_connection.write_message(json.dumps(result_message))
