import os
import json
import time
import shutil
import glob

import mimetypes
mimetypes.init()

def get_mime_type(full_filename):
    "Returns the mimetype for a file given its fully qualified filename."
    mime, encoding = mimetypes.guess_type(full_filename)
    return mime

from rayage_ws import messageHandler
from ClangCompiler import ClangCompiler
from constants import *

from ProjectRunner import ProjectRunner

@messageHandler("project_list_request")
def handle_project_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available projects to work on to our socket.
    Currently a flat list of folders in the STUDENTS_DIR
    """
    projects = [{'label': p, 'id': p} for p in os.listdir(socket_connection.user_dir()) 
                                      if os.path.isdir(socket_connection.user_dir(p))]
                                      
    result_message = {'type': 'project_list',
                      'projects': projects}
    socket_connection.write_message(json.dumps(result_message))
    
@messageHandler("close_project_request")
def handle_close_project(socket_connection, message, notify=True):
    """
    Sets the current project for the given socket_connection to None and returns an
    acknowledgement that the project has been closed.
    """
    socket_connection.project = None
    result_message = {'type': 'close_project_acknowledge'}
    socket_connection.write_message(json.dumps(result_message))
    if notify:
        socket_connection.notify("You've closed your project!", "success")

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
    
@messageHandler("file_type_list_request")
def handle_file_type_list_request(socket_connection, message):
    """
    Writes a JSON structure representing the available file types which may be created to our socket.
    """                
    types = [{'label': t, 'id': t} for t in PROJECT_DATA_EXTENSIONS]
         
    result_message = {'type': 'file_type_list',
                      'types': types}
                      
    socket_connection.write_message(json.dumps(result_message))

@messageHandler("new_project_request", ["name", "template"])
def handle_new_project_request(socket_connection, message):
    """
    Handles new project requests by creating a directory in the user's projects folder.

    TODO:
    Send proper responses
    """
    name = message["name"]
    template = message["template"]

    try:
        new_project_dir = socket_connection.user_dir(name)
        if template:
            shutil.copytree(os.path.join(TEMPLATES_DIR, template), new_project_dir)
        else:
            os.makedirs(new_project_dir)

        socket_connection.notify("You made a new project!", "success")
        handle_open_project_request(socket_connection, {'id': name}, False)
    except shutil.Error as e:
        # copytree error
        # This exception collects exceptions that are raised during a multi-file operation. 
        # For copytree(), the exception argument is a list of 3-tuples (srcname, dstname, exception).
        # TODO: Double check this. Existing project folder always falls into OSError.
        socket_connection.notify("Unknown project template.", "error")
    except OSError as e:
        # makedirs error
        socket_connection.notify("Project already exists.", "error")

@messageHandler("open_project_request", ["id"])
def handle_open_project_request(socket_connection, message, notify=True):
    """
    Handles open project requests by setting the project attribute of the users connection and sending a project state to the client.
    """
    project_id = message['id']
    
    project_dir = socket_connection.user_dir(project_id)

    if project_dir is None:
        return #TODO: generic error message

    if not os.path.isdir(project_dir):
        return #TODO: unknown project
        
    socket_connection.project = project_id
    
    def is_project_file(filename):
        root, ext = os.path.splitext(filename)
        return ext in PROJECT_DATA_EXTENSIONS
    
    project_files = filter(is_project_file, os.listdir(project_dir))
    
    project_file_data = []
    for filename in project_files:
        with open(os.path.join(project_dir, filename), "r") as f:
            project_file_data.append({'filename': filename, 
                                      'mimetype': get_mime_type(os.path.join(project_dir, filename)),
                                      'data': f.read(), 
                                      'modified': False, 
                                      'undo_data': None})
    
    project_state = {'type': 'project_state',
                     'id': project_id,
                     'files': project_file_data}
    
    socket_connection.write_message(json.dumps(project_state))
    if notify:
        socket_connection.notify("You've opened %s!" % socket_connection.project, "success")

@messageHandler("new_file_request", ["name", "filetype"])
def handle_new_file_request(socket_connection, message):
    """
    Handles new file requests - does not allow overwriting files.
    """
    filename = "%s%s" % (message['name'], message['filetype'])
    dst = socket_connection.project_dir(filename)

    if not dst:
        socket_connection.notify("You need a project open!", "error")
        return

    if os.path.exists(dst):
        socket_connection.notify("%s already exists!" % filename, "error")
        return

    file(dst, 'w').close()
    # reopen the project with newly created file.
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just created %s!" % filename, "success")

@messageHandler("delete_project_request", [])
def handle_delete_project_request(socket_connection, message):
    src = socket_connection.project_dir()
    # move to trash
    # trash/username/projectname/timestamp/
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    shutil.move(src, dst)
    # notify on deletion and close their windows
    socket_connection.notify("You just deleted %s." % socket_connection.project, "success")
    handle_close_project(socket_connection, {}, False)

@messageHandler("delete_file_request", ["file"])
def handle_delete_file_request(socket_connection, message):
    f = message["file"]
    src = socket_connection.project_dir(f)
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.move(src, dst)

    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just deleted %s." % f, "success")

@messageHandler("build_project_request", [])
def handle_build_project_request(socket_connection, message):
    if socket_connection.project_dir():
        # we might only need one of these? do we get more/better multiprocessing this way?
        c = ClangCompiler()
        cpp_files = list(glob.glob(socket_connection.project_dir("*.cpp")))
        c.compile(cpp_files, socket_connection.project_dir("a.out"))

        if len(c.errors()):
            # return compiler errors
            errors = {"type": "build_error_list", "errors": c.errors()}
            socket_connection.write_message(json.dumps(errors))
        else:
            # return success message (possibly pass to build).
            socket_connection.notify("You just built %s." % socket_connection.project, "success")




@messageHandler("run_stdin_data", ["data"])
def handle_run_stdin_data(socket_connection, message):
    data = message['data']

    if socket_connection.project_runner is None:
        socket_connection.notify("There is no project running. Nowhere to send input.", "error")
        return
        
    socket_connection.project_runner.queue_input(data)

@messageHandler("run_project_request", ["args"])
def handle_run_project_request(socket_connection, message):
    args = message['args']
    executable = socket_connection.project_dir("a.out")
    
    print "run_project_request:", executable, " with args:", args
    
    if socket_connection.project_runner is not None:
        socket_connection.notify("This project is already running! Check the run console.", "error")
        return
    
    if not os.path.exists(executable):
        socket_connection.notify("The project must be built before running!", "error")
        return
    
    def stdout_cb(data):
        socket_connection.notify(data, "info")
    
    def stderr_cb(data):
        socket_connection.notify(data, "error")
    
    def exited_cb(return_value):
        socket_connection.notify("{} exited with return value of {}".format(executable, return_value), "info")
        socket_connection.project_runner = None
    
    socket_connection.project_runner = ProjectRunner(executable, args, stdout_cb, stderr_cb, exited_cb)
    socket_connection.project_runner.start()
    
