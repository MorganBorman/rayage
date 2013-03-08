import json

from constants import *
from ws_exceptions import *

from rayage.database.User import User

from CASVerifiedRequestHandler import CASVerifiedRequestHandler

class DownloadHandler(CASVerifiedRequestHandler):
    "Tornado request handler to deal with downloads."
    download_handlers = {}
    
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
    
    def get(self, download_type, download_selector):
        if self.get_current_user() is None:
            self.validate_user()
            return
            
        try:    
            if download_type in self.download_handlers.keys():
                self.download_handlers[download_type](self, download_selector)
            else:
                self.send_error(404)
        except InsufficientPermissions:
            self.send_error(550)
            
class downloadHandler(object):
    "Decorator to attach handlers for specific upload paths."
    def __init__(self, download_type, minimum_permission_level=PERMISSION_LEVEL_USER):
        self.download_type = download_type
        self.minimum_permission_level = minimum_permission_level

    def __call__(self, f):
        if type(f) == type:
            f = f()
        
        def handler(request_handler, download_selector):
            if self.minimum_permission_level > request_handler.permission_level:
                raise InsufficientPermissions()
                
            f(request_handler, download_selector)
        
        self.handler = handler
        
        DownloadHandler.download_handlers[self.download_type] = handler
        
        return f
