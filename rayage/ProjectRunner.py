"""
A class which runs a specified executable using subprocess.
Polls for stdout stderr data in a thread and uses specified callbacks to return data from these.
Provides a method by which stdin data may be queued to pipe to the running program.
"""

import subprocess
import threading
import select
import pty
import sys
import os

check_has_sandbox_support = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HasSandboxSupport.py")
HAS_SANDBOX_SUPPORT = (subprocess.call(["python", check_has_sandbox_support]) == 0)

if not HAS_SANDBOX_SUPPORT:
    sys.stderr.write("Modules (or the correct module versions) necessary for sandboxing project runs were not found.\n")
    sys.stderr.write("Projects can still be run but without sandboxing. PROCEED WITH CAUTION.\n")

class ProjectRunner(threading.Thread):
    def __init__(self, path, args, stdout_cb, stderr_cb, exited_cb, timeout_cb, timeout=15):
        threading.Thread.__init__(self)
        
        self.path = os.path.abspath(path)
        
        if HAS_SANDBOX_SUPPORT:
            self.sandboxpy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MiniSandbox.py")
            self.arguments = ["python", self.sandboxpy, os.path.dirname(self.path), self.path]
        else:
            self.sandboxpy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NoSandbox.py")
            self.arguments = ["python", self.sandboxpy, os.path.dirname(self.path), self.path]
        
        self.arguments.extend(args)
        
        self.master, slave = pty.openpty()
        
        self.proc = subprocess.Popen(self.arguments, stdin=slave, stdout=slave, stderr=subprocess.PIPE, close_fds=True)
        
        self.stdout_cb = stdout_cb
        self.stderr_cb = stderr_cb
        self.exited_cb = exited_cb
        self.timeout_cb = timeout_cb
        
        self.timeout = timeout
        
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
            
            if self.cpu_seconds() > self.timeout and self.proc.poll() is None:
                print "cpu_seconds = {}".format(self.cpu_seconds())
                self.proc.terminate()
                self.timeout_cb()
            
            if len(self.input_queue) > 0:
                os.write(self.master, self.input_queue.pop(0))
            
            return_value = self.proc.poll()
        
        while self.process_pipes():
            pass
        
        self.exited_cb(return_value)
        
    def cpu_seconds(self):
        args = ['ps', '-o"%x"', '--no-headers', '-p', str(self.proc.pid)]
        
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        
        output = output.strip('"').rstrip('"\n')
        
        cpu_hours, cpu_minutes, cpu_seconds = map(int, output.split(":"))
        
        cpu_seconds = (60*60*cpu_hours) + (60*cpu_minutes) + cpu_seconds
        
        return cpu_seconds
