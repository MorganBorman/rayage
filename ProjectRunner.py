"""
A class which runs a specified executable using subprocess.
Polls for stdout stderr data in a thread and uses specified callbacks to return data from these.
Provides a method by which stdin data may be queued to pipe to the running program.
"""

import subprocess
import threading
import select
import pty
import os

class ProjectRunner(threading.Thread):
    def __init__(self, path, args, stdout_cb, stderr_cb, exited_cb):
        threading.Thread.__init__(self)
        
        self.path = path
        self.arguments = [path]
        self.arguments.extend(args)
        
        self.master, slave = pty.openpty()
        
        self.proc = subprocess.Popen(self.arguments, stdin=slave, stdout=slave, stderr=subprocess.PIPE, close_fds=True)
        
        self.stdout_cb = stdout_cb
        self.stderr_cb = stderr_cb
        self.exited_cb = exited_cb
        
        self.input_queue = []
        
    def queue_input(self, data):
        self.input_queue.append(data)
        
    def process_pipes(self):
        outputs, _, _ = select.select([self.master, self.proc.stderr], [], [], 1.0)
        
        gotdata = False
        
        if outputs is not None:
            for output in outputs:
                if output == self.master:
                    data = os.read(self.master, 1024)
                    if len(data) > 0:
                        gotdata = True
                        self.stdout_cb(data)
                elif output == self.proc.stderr:
                    data = self.proc.stderr.read(1024)
                    if len(data) > 0:
                        gotdata = True
                        self.stderr_cb(data)
        
        return gotdata
        
    def run(self):
        return_value = self.proc.poll()
        while return_value is None:
            self.process_pipes()
            
            if len(self.input_queue) > 0:
                os.write(self.master, self.input_queue.pop(0))
            
            return_value = self.proc.poll()
        
        while self.process_pipes():
            pass
        
        self.exited_cb(return_value)
