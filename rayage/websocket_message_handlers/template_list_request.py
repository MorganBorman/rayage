from constants import *
import os
import json
from ..WebSocketHandler import messageHandler

@messageHandler("template_list_request")
def handle_template_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available templates to our socket.
    Currently a flat list of folders in the TEMPLATES_DIR

    TODO:
    Use a "real" id of some sort (at least remove problematic chars)

    """
    templates = [{'label': t, 'id': t} for t in os.listdir(TEMPLATES_DIR) 
                                       if os.path.isdir(os.path.join(TEMPLATES_DIR, t))]
    templates.insert(0, {'label': 'Empty Template', 'id': ''})

    result_message = {'type': 'template_list', 
                      'templates': templates}
    socket_connection.write_message(json.dumps(result_message))
