#!/usr/bin/env python
################################################################################
# The Sandbox Libraries (Python) - Sample Script                               #
#                                                                              #
# Copyright (C) 2009-2012 LIU Yu, <pineapple.liu@gmail.com>                    #
# All rights reserved.                                                         #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided that the following conditions are met:  #
#                                                                              #
# 1. Redistributions of source code must retain the above copyright notice,    #
#    this list of conditions and the following disclaimer.                     #
#                                                                              #
# 2. Redistributions in binary form must reproduce the above copyright notice, #
#    this list of conditions and the following disclaimer in the documentation #
#    and/or other materials provided with the distribution.                    #
#                                                                              #
# 3. Neither the name of the author(s) nor the names of its contributors may   #
#    be used to endorse or promote products derived from this software without #
#    specific prior written permission.                                        #
#                                                                              #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"  #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE    #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE   #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE     #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR          #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF         #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS     #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN      #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)      #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                                  #
################################################################################
# 
# Modifed to add limited support for the 'open' syscall with restrictions
# on where files may be opened.

import os
import sys
import os.path
import traceback

try:
    # check platform type
    system, machine = os.uname()[0], os.uname()[4]
    if system not in ('Linux', ) or machine not in ('i686', 'x86_64', ):
        raise AssertionError("Unsupported platform type.\n")
        
    # check package availability / version
    import sandbox
    if not hasattr(sandbox, '__version__') or sandbox.__version__ < "0.3.4-3":
        raise AssertionError("Unsupported sandbox version.\n")
        
    from sandbox import *
except ImportError:
    sys.stderr.write("Required package(s) missing.\n")
    sys.exit(os.EX_UNAVAILABLE)
    
except AssertionError as e:
    sys.stderr.write(str(e))
    sys.exit(os.EX_UNAVAILABLE)

# result code translation
def result_name(r):
    return ('PD', 'OK', 'RF', 'ML', 'OL', 'TL', 'RT', 'AT', 'IE', 'BP')[r] \
        if r in range(10) else None

# mini sandbox with embedded policy
class MiniSandbox(SandboxPolicy,Sandbox):
    sc_table = None
    
    # white list of essential linux syscalls for statically-linked C programs
    sc_safe = {'i686': set([0, 3, 4, 5, 6, 19, 45, 54, 90, 91, 122, 125, 140, 163, 192, 197, 224, 243, 252, ]),
               'x86_64': set([0, 1, 2, 3, 5, 8, 9, 10, 11, 12, 16, 25, 63, 158, 219, 231, ])}
    # open() system call abi
    SC_open = (2, ) if machine == 'x86_64' else (5, )
    
    def __init__(self, *args, **kwds):
        # initialize table of system call rules
        self.sc_table = [self._KILL_RF, ] * 1024
        for scno in MiniSandbox.sc_safe[machine]:
            self.sc_table[scno] = self._CONT
            
        # special rules for open()
        for scno in MiniSandbox.SC_open:
            self.sc_table[scno] = self.SYS_open
            
        self.sandbox_directory = None
        
        # initialize as a polymorphic sandbox-and-policy object
        SandboxPolicy.__init__(self)
        Sandbox.__init__(self, *args, **kwds)
        self.policy = self
        
    def probe(self):
        # add custom entries into the probe dict
        d = Sandbox.probe(self, False)
        d['cpu'] = d['cpu_info'][0]
        d['mem'] = d['mem_info'][1]
        d['result'] = result_name(self.result)
        return d
    
    def __call__(self, e, a):
        # handle SYSCALL/SYSRET events with local rules
        if e.type in (S_EVENT_SYSCALL, S_EVENT_SYSRET):
            if machine == 'x86_64' and e.ext0 != 0:
                return self._KILL_RF(e, a)
            return self.sc_table[e.data](e, a)
        # bypass other events to base class
        return SandboxPolicy.__call__(self, e, a)
    
    def SYS_open(self, e, a): # open()
        try:
            assert(e.data in MiniSandbox.SC_open)
            if e.type == S_EVENT_SYSCALL:
                value = self.dump(T_STRING, e.ext1)
                path = os.path.dirname(os.path.abspath(value))
                common_path = os.path.commonprefix([path, self.sandbox_directory])
                if not os.path.samefile(common_path, self.sandbox_directory):
                    print ">> Killed because of open() outside sandbox."
                    return self._KILL_RF(e, a)
        except:
            traceback.print_exc()
            return self._KILL_BP(e, a)
        return self._CONT(e, a)
    
    def _CONT(self, e, a): # continue
        a.type = S_ACTION_CONT
        return a
    
    def _KILL_RF(self, e, a): # restricted func.
        a.type, a.data = S_ACTION_KILL, S_RESULT_RF
        return a
    
    def _KILL_BP(self, e, a): # bad policy
        a.type, a.data = S_ACTION_KILL, S_RESULT_BP
        return a

def main(args):
    # sandbox configuration
    
    # get and set the CWD to the directory to sandbox the program into
    sandbox_directory = os.path.abspath(args[1])
    os.chdir(sandbox_directory)
    
    cookbook = {  
        'args': args[2:],                       # targeted program
        'stdin': sys.stdin,                     # input to targeted program
        'stdout': sys.stdout,                   # output from targeted program
        'stderr': sys.stderr,                   # error from targeted program
        'quota': dict(wallclock = 60*60*1000,   # 1 hour
                      cpu = 15000,              # 5 sec
                      memory = 8388608,         # 8 MB
                      disk = 1048576)}          # 1 MB
    
    # create a sandbox instance and execute till end
    msb = MiniSandbox(**cookbook)
    msb.sandbox_directory = sandbox_directory
    msb.run()
    # verbose statistics (write these back over a UDS in the future)
    #sys.stderr.write(">> result: %(result)s\n>> cpu: %(cpu)dms\n>> mem: %(mem)dkB\n" % \
    #    msb.probe())
    return os.EX_OK

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("synopsis: python " + __file__ + "foo/ foo/a.out arg1 arg2\n")
        sys.exit(os.EX_USAGE)
    sys.exit(main(sys.argv))
