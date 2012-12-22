from constants import *
import json

from ..database.User import User
from ..database.SessionFactory import SessionFactory

from ..WebSocketHandler import messageHandler

@messageHandler("close_project_request")
def handle_close_project_request(socket_connection, message, notify=True):
    """
    Sets the current project for the given socket_connection to None and returns an
    acknowledgement that the project has been closed.
    """
    socket_connection.project = None
    
    username = socket_connection.user.username
    session = SessionFactory()
    try:
        socket_connection.user.current_project = None
        session.add(socket_connection.user)
        session.commit()
    finally:
        session.close()
    #TODO: fix this hack! the attribute refresh operation does not succeed so
    #      a new instance of user has to be assigned to the socket connection
    socket_connection.user = User.get_user(username)
    
    result_message = {'type': 'close_project_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))
    if notify:
        socket_connection.notify("You've closed your project!", "success")
