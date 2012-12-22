from constants import *
import json
from ..WebSocketHandler import messageHandler

@messageHandler("file_type_list_request")
def handle_file_type_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available file types which may be created to our socket.
    """                
    types = [{'label': t, 'id': t} for t in PROJECT_DATA_EXTENSIONS]
         
    result_message = {'type': 'file_type_list',
                      'types': types}
                      
    socket_connection.write_message(json.dumps(result_message))
