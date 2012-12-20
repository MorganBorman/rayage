import os
import sys

try:
    # check platform type
    system, machine = os.uname()[0], os.uname()[4]
    if system not in ('Linux', ) or machine not in ('i686', 'x86_64', ):
        raise AssertionError("Unsupported platform type.\n")
        
    # check package availability / version
    import sandbox
    if not hasattr(sandbox, '__version__') or sandbox.__version__ < "0.3.4-3":
        raise AssertionError("Unsupported sandbox version.\n")
        
    sys.exit(os.EX_OK)

except ImportError:
    sys.exit(os.EX_UNAVAILABLE)

except AssertionError as e:
    sys.stderr.write(str(e))
    sys.exit(os.EX_UNAVAILABLE)
