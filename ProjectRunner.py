"""
A class which runs a specified executable using subprocess.
Polls for stdout stderr data in a thread and uses specified callbacks to return data from these.
Provides a method by which stdin data may be queued to pipe to the running program.
"""

import subprocess
import threading
import select

class ProjectRunner(threading.Thread):
    def __init__(self, path, args, stdout_cb, stderr_cb, exited_cb):
        threading.Thread.__init__(self)
        
        self.path = path
        self.proc = subprocess.Popen([path].extend(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.stdout_cb = stdout_cb
        self.stderr_cb = stderr_cb
        self.exited_cb = exited_cb
        
        self.input_queue = []
        
    def queue_input(self, data):
        self.input_queue.append(data)
        
    def run(self):
        return_value = self.proc.poll()
        while return_value is None:
            outputs, inputs, _ = select.select([self.proc.stdout, self.proc.stderr], [self.proc.stdin], [], 1.0)
            
            if outputs is not None:
                for output in outputs:
                    if output == self.proc.stdout:
                        self.stdout_cb(self.proc.stdout.read())
                    elif output == self.proc.stderr:
                        self.stderr_cb(self.proc.stderr.read())
            
            if inputs is not None and len(self.input_queue) > 0:
                stdin = inputs[0]
                self.proc.stdin.write(self.input_queue.pop(0))
            
            return_value = self.proc.poll()
        
        self.exited_cb(return_value)
