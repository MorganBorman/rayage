import os.path
import glob

upload_handlers_init = os.path.abspath(__file__)
upload_handlers_dir = os.path.dirname(upload_handlers_init)

filenames = glob.glob(os.path.join(upload_handlers_dir, "*.py"))

for filename in filenames:
    module_name, _py = os.path.splitext(os.path.basename(filename))
    
    # Don't try to load __init__.py
    if module_name == "__init__":
        continue
    
    __import__('rayage.upload_handlers.{}'.format(module_name))
