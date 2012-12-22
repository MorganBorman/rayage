from constants import *
import os.path
import shlex
import json
from ..ProjectRunner import ProjectRunner
from ..WebSocketHandler import messageHandler

@messageHandler("run_project_request", ["args"])
def handle_run_project_request(socket_connection, message):
    args = shlex.split(message['args'])
    executable = socket_connection.project_dir("a.out")
    
    print "run_project_request:", executable, " with args:", args
    
    if socket_connection.project_runner is not None:
        socket_connection.notify("This project is already running! Check the run console.", "error")
        return
    
    if not os.path.exists(executable):
        socket_connection.notify("The project must be built before running!", "error")
        return
    
    def stdout_cb(data):
        result_message = {'type': 'run_stdout_data', 
                          'data': data}
        socket_connection.write_message(json.dumps(result_message))
    
    def stderr_cb(data):
        result_message = {'type': 'run_stderr_data', 
                          'data': data}
        socket_connection.write_message(json.dumps(result_message))
    
    def exited_cb(return_value):
        socket_connection.notify("{} exited with return value of {}".format(executable, return_value), "info")
        socket_connection.project_runner = None
        
    def timeout_cb():
        socket_connection.notify("Your program was taking too long to run. Check your loops.", "error")
    
    socket_connection.project_runner = ProjectRunner(executable, args, stdout_cb, stderr_cb, exited_cb, timeout_cb)
    socket_connection.project_runner.start()
    socket_connection.log("debug","has run project \"{}\"".format(socket_connection.project))
