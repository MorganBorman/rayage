from constants import *
import json
import glob

from ClangCompiler import ClangCompiler
from ..WebSocketHandler import messageHandler

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
