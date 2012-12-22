from constants import *
from ..WebSocketHandler import messageHandler

@messageHandler("run_stdin_data", ["data"])
def handle_run_stdin_data(socket_connection, message):
    data = message['data']

    if socket_connection.project_runner is None:
        socket_connection.notify("There is no project running. Nowhere to send input.", "error")
        return
        
    socket_connection.project_runner.queue_input(data)
