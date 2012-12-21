import os
import json
import time
import shutil
import glob
import shlex

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

from database.User import User
from database.SessionFactory import SessionFactory

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
    if template == "": template_name = "empty template"
    else: template_name = template
    	
    try:
        new_project_dir = socket_connection.user_dir(name)

        # verify the project will end up in the user's directory
        if os.path.dirname(os.path.normpath(new_project_dir)) != os.path.normpath(socket_connection.user_dir()):
            socket_connection.notify("%s is an illegal project name!" % name, "error")
            return

        if template:
            shutil.copytree(os.path.join(TEMPLATES_DIR, template), new_project_dir)
        else:
            os.makedirs(new_project_dir)
            
        socket_connection.log("debug","Has created new project called \"{}\" from template \"{}\"".format(name,template_name))
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
def handle_open_project_request(socket_connection, message, notify=True, selected=""):
    """
    Handles open project requests by setting the project attribute of the users connection and sending a project state to the client.
    """
    project_id = message['id']
    
    if project_id != socket_connection.user.current_project:
        username = socket_connection.user.username
        
        session = SessionFactory()
        try:
            socket_connection.user.current_project = project_id
            session.add(socket_connection.user)
            session.commit()
        finally:
            session.close()
        #TODO: fix this hack! the attribute refresh operation does not succeed so
        #      a new instance of user has to be assigned to the socket connection
        socket_connection.user = User.get_user(username)
    
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
        # create state files if they don't exist for some reason.
        if not os.path.exists(os.path.join(project_dir, "%s.swp" % filename)):
            dst = socket_connection.project_dir("%s.swp" % filename)
            src = socket_connection.project_dir(filename)
            shutil.copyfile(src, dst)
        if not os.path.exists(os.path.join(project_dir, "%s~" % filename)):
            open(os.path.join(project_dir, "%s~" % filename), 'w').close()

        with \
        open(os.path.join(project_dir, filename), "r") as file,\
        open(os.path.join(project_dir, "%s.swp" % filename), "r") as swap,\
        open(os.path.join(project_dir, "%s~" % filename), "r") as undo:
            f, s, u = (file.read(), swap.read(), undo.read())
            project_file_data.append({'filename': filename, 
                                      'mimetype': get_mime_type(os.path.join(project_dir, filename)),
                                      'data': s,
                                      'modified': f != s,
                                      'undo_data': json.loads(u or "null"),
                                      'selected': selected == filename})
    
    project_state = {'type': 'project_state',
                     'id': project_id,
                     'files': project_file_data}
    
    socket_connection.write_message(json.dumps(project_state))

    socket_connection.log("debug","has opened project \"{}\"".format(project_id))
    if notify:
        socket_connection.notify("You've opened %s!" % socket_connection.project, "success")

@messageHandler("project_state_push", ["files"])
def handle_project_state_push(socket_connection, message):
    if socket_connection.project is None:
        socket_connection.notify("There's been a catastrophic failure. Please manually save any data to your local machine (copy/paste) and refresh.", "error")
        return

    for file in message['files']:
        socket_connection.log("debug","has pushed state for file \"{}\"".format(file['filename']))
        # if modified, overwrite the .swp file with new data
        if file['modified']:
            with open(socket_connection.project_dir("%s.swp" % file['filename']), 'w+') as f:
                f.write(file['data'])

        # overwrite the undo history - stored as JSON in FILENAME.cpp~
        with open(socket_connection.project_dir("%s~" % file['filename']), 'w+') as f:
            f.write(json.dumps(file['undo_data']))

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

    # verify the file will end up in the user's directory
    if os.path.dirname(os.path.normpath(dst)) != os.path.normpath(socket_connection.project_dir()):
        socket_connection.notify("%s is an illegal filename!" % filename, "error")
        return

    file(dst, 'w').close()
    file("%s.swp" % dst, 'w').close()
    file("%s~" % dst, 'w').close()

    # reopen the project with newly created file.
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.log("debug","has created file \"{}\"".format(filename))
    socket_connection.notify("You just created %s!" % filename, "success")

@messageHandler("save_file_request", ["filename"])
def handle_save_file_request(socket_connection, message):
    filename = message['filename']
    src = socket_connection.project_dir("%s.swp" % filename)
    dst = socket_connection.project_dir(filename)
    shutil.copyfile(src, dst)
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.notify("You just saved %s!" % filename, "success")
    socket_connection.log("debug","has saved file \"{}\"".format(filename))
    
@messageHandler("revert_file_request", ["filename"])
def handle_open_file_request(socket_connection, message):
    filename = message['filename']
    dst = socket_connection.project_dir("%s.swp" % filename)
    src = socket_connection.project_dir(filename)
    shutil.copyfile(src, dst)
    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False, filename)
    socket_connection.notify("You just reverted %s!" % filename, "success")
    socket_connection.log("debug","has reverted file \"{}\"".format(filename))

@messageHandler("delete_project_request", [])
def handle_delete_project_request(socket_connection, message):
    src = socket_connection.project_dir()
    # move to trash
    # trash/username/projectname/timestamp/
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    shutil.move(src, dst)
    # notify on deletion and close their windows
    socket_connection.notify("You just deleted %s." % socket_connection.project, "success")
    socket_connection.log("debug","has deleted project \"{}\"".format(socket_connection.project))
    handle_close_project(socket_connection, {}, False)

@messageHandler("delete_file_request", ["file"])
def handle_delete_file_request(socket_connection, message):
    f = message["file"]
    src = socket_connection.project_dir(f)
    dst = os.path.join(TRASH_DIR, socket_connection.username, socket_connection.project, str(int(time.time())))
    if not os.path.exists(dst):
        os.makedirs(dst)
    shutil.move(src, dst)
    shutil.move(src+".swp", dst)
    shutil.move(src+"~", dst)

    handle_open_project_request(socket_connection, {'id': socket_connection.project}, False)
    socket_connection.notify("You just deleted %s." % f, "success")
    socket_connection.log("debug","has deleted file \"{}\"".format(f))

@messageHandler("build_project_request", [])
def handle_build_project_request(socket_connection, message):
    if socket_connection.project:
        # ClangCompiler basically just encapsulates a few functions
        # It spawns off a subprocess for clang++.
        c = ClangCompiler()
        cpp_files = list(glob.glob(socket_connection.project_dir("*.cpp")))
        c.compile(cpp_files, socket_connection.project_dir("a.out"))

        if len(c.errors()):
            # return compiler errors
            errors = {"type": "build_error_list", "errors": c.errors()}
            socket_connection.notify("You had build errors...", "error")
            socket_connection.write_message(json.dumps(errors))
        else:
            # return success message (possibly pass to build).
            socket_connection.notify("You just built %s." % socket_connection.project, "success")
            socket_connection.log("debug","has built project \"{}\"".format(socket_connection.project))




@messageHandler("run_stdin_data", ["data"])
def handle_run_stdin_data(socket_connection, message):
    data = message['data']

    if socket_connection.project_runner is None:
        socket_connection.notify("There is no project running. Nowhere to send input.", "error")
        return
        
    socket_connection.project_runner.queue_input(data)

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
    
