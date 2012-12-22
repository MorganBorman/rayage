import os.path
#import imp
import glob

ws_msg_handler_init = os.path.abspath(__file__)
ws_msg_handler_dir = os.path.dirname(ws_msg_handler_init)

filenames = glob.glob(os.path.join(ws_msg_handler_dir, "*.py"))

for filename in filenames:
    module_name, _py = os.path.splitext(os.path.basename(filename))
    
    # Don't try to load __init__.py
    if module_name == "__init__":
        continue
    
    #module = imp.load_source('rayage.websocket_message_handlers.{}'.format(module_name), filename)
    __import__('rayage.websocket_message_handlers.{}'.format(module_name))
