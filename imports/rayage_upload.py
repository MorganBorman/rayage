import json

from constants import *
from ws_exceptions import *

from database.User import User

from CASVerifiedRequestHandler import CASVerifiedRequestHandler

class UploadHandler(CASVerifiedRequestHandler):
    upload_handlers = {}
    
    @property
    def permission_level(self):
        """
        Returns the permission_level associated with this connection.
        """
        username = self.get_current_user()
        user = User.get_user(username)
        
        if user is not None:
            return user.permission_level
        return PERMISSION_LEVEL_NONE
    
    def post(self, upload_type):
        if self.get_current_user() is None:
            self.validate_user()
            return
            
        if upload_type in self.upload_handlers.keys():
            self.upload_handlers[upload_type](self)
            
class uploadHandler(object):
    def __init__(self, upload_type, minimum_permission_level=PERMISSION_LEVEL_USER):
        self.upload_type = upload_type
        self.minimum_permission_level = minimum_permission_level

    def __call__(self, f):
        if type(f) == type:
            f = f()
        
        def handler(request_handler):
            if self.minimum_permission_level > request_handler.permission_level:
                raise InsufficientPermissions()
                
            f(request_handler)
        
        self.handler = handler
        
        UploadHandler.upload_handlers[self.upload_type] = handler
        
        return f
        

