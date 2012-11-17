import os
import sys
import json
import time
import random
import tempfile
import zipfile
import traceback

from sqlalchemy import func
import sqlalchemy

from rayage_ws import messageHandler, WebSocketHandler
from rayage_upload import uploadHandler
from constants import *
from ws_exceptions import *
from RayageJsonStoreHandler import RayageJsonStoreHandler

from database.User import User
from database.SessionFactory import SessionFactory

from DojoQuery import DojoQuery
from DojoSort import DojoSort

admin_modules = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder', 'iconClass': 'modules'},
    { 'id': 'view_statistics', 'name': 'View Statistics', 'type': 'custom/StatisticsViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'view_statistics'},
    { 'id': 'user_manager', 'name': 'Manage Users', 'type': 'custom/UserManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'users'},
    { 'id': 'template_manager', 'name': 'Manage Templates', 'type': 'custom/TemplateManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'templates'},
]

@messageHandler("admin_module_tree_request", minimum_permission_level=PERMISSION_LEVEL_TA)
def handle_admin_module_tree_request(socket_connection, message):
    """
    Writes a JSON structure representing the available admin modules tree to our socket.
    """                                
    result_message = {'type': 'admin_module_tree',
                      'modules': admin_modules}
                      
    socket_connection.write_message(json.dumps(result_message))

@messageHandler("RayageJsonStore/Users", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class UserStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the users and their permissions.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        RayageJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
        def after_insert_listener(mapper, connection, target):
            result_message = {'type': "RayageJsonStore/Users",
                              'action': 'create',
                              'object': {'id': target.id, 'username': target.username, 'permissions': target.permission_level},
                             }
            
            self.publish(json.dumps(result_message))

        sqlalchemy.event.listen(User, 'after_insert', after_insert_listener)
        
        def after_update_listener(mapper, connection, target):
            result_message = {'type': "RayageJsonStore/Users",
                              'action': 'update',
                              'object': {'id': target.id, 'username': target.username, 'permissions': target.permission_level},
                             }
            
            self.publish(json.dumps(result_message))

        sqlalchemy.event.listen(User, 'after_update', after_update_listener)
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(User.id, User.username, User.permission_level)
        
            column_map = {u'id': User.id, u'username': User.username, u'permissions': User.permission_level}
        
            if dojo_query is not None:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            user_count = query.count()
            user_list = query.offset(start).limit(count).all()
            user_list = [{'id': uid, 'username': username, 'permissions': permission_level} for uid, username, permission_level in user_list]
            
            result_message = {'type': message[u'type'],
                              'response': user_list,
                              'total': user_count,
                              'deferredId': message['deferredId'],
                             }
        finally:
            session.close()
        
        socket_connection.write_message(json.dumps(result_message))
        
    def put(self, socket_connection, message, object_data):
            
        target_permission_level = int(object_data[u'permissions'])
            
        session = SessionFactory()
        try:
            if target_permission_level >= socket_connection.permission_level and not socket_connection.permission_level == PERMISSION_LEVEL_ADMIN:
                raise InsufficientPermissions("Cannot elevate user permissions higher than self.")
            
            user = User.get_user(object_data[u'username'])
            user.permission_level = target_permission_level
            
            session.add(user)
            session.commit()
        finally:
            session.close()
            
        result_message = {'type': message[u'type'],
                          'response': [],
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
        
@messageHandler("RayageJsonStore/Templates", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class TemplateStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the templates.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        RayageJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        """
        wm = pyinotify.WatchManager()
        
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_ONLYDIR | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM  # watched events

        class EventHandler(pyinotify.ProcessEvent):
            def process_IN_CREATE(self, event):
                print "Creating:", event.pathname
                on_change(event.pathname, 'create')

            def process_IN_DELETE(self, event):
                print "Deleting:", event.pathname
                on_change(event.pathname, 'delete')
                
            def process_IN_MOVED_FROM(self, event):
                print "Moved From:", event.pathname
                on_change(event.pathname, 'delete')
                
            def process_IN_MOVED_TO(self, event):
                print "Moved To:", event.pathname
                on_change(event.pathname, 'create')
                
        notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
        # Start the notifier from a new thread, without doing anything as no directory or file are currently monitored yet.
        notifier.start()
        # Start watching a path
        wdd = wm.add_watch(TEMPLATES_DIR, mask, rec=False)
        """
        
    def on_change(self, pathname, action):
        t = os.path.basename(pathname)
        
        result_message = {'type': "RayageJsonStore/Templates",
                          'action': action,
                          'object': {'id': t, 'name': t},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
    
        template_list = [{'id': t, 'name': t} for t in os.listdir(TEMPLATES_DIR) 
                                           if os.path.isdir(os.path.join(TEMPLATES_DIR, t))]
            
        template_count = len(template_list)
            
        result_message = {'type': message[u'type'],
                          'response': template_list,
                          'total': template_count,
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
        
print TemplateStoreHandler
        
@uploadHandler('template', PERMISSION_LEVEL_PROF)
def template_upload_handler(request_handler):
    if u'uploadedfiles[]' in request_handler.request.files.keys():
        file_info = request_handler.request.files[u'uploadedfiles[]'][0]
        response_data = {'file': file_info[u'filename'], 'type': file_info[u'content_type'], 'size': len(file_info[u'body'])}
        
        try:
            uploaded_files = request_handler.request.files[u'uploadedfiles[]']
            
            for uploaded_file in uploaded_files:
                
                with tempfile.TemporaryFile(mode='w+b') as tfile:
                    filename = uploaded_file['filename']
                    content_type = uploaded_file['content_type']
                    
                    # Write the template archive (hopefully an archive) to the temp file
                    tfile.write(uploaded_file['body'])
                    # Reset the file position
                    tfile.seek(0)
                    
                    if zipfile.is_zipfile(tfile):
                        zfile = zipfile.ZipFile(tfile)
                        
                        namelist = zfile.namelist()
                        
                        if len(namelist) == 0:
                            raise Exception("Cannot install empty project template.")
                        
                        if not '/' in namelist[0]:
                            raise Exception("All template files must be contained in a single directory within the zip file.")
                        
                        template_dir_prefix = namelist[0].split('/')[0]
                        
                        for name in namelist:
                            if namelist[0].split('/')[0] != template_dir_prefix:
                                raise Exception("All template files must be contained in a single directory within the zip file.")
                        
                        zfile.extractall(TEMPLATES_DIR)
                        
                        TemplateStoreHandler.on_change(template_dir_prefix, 'create')
        except Exception, e:
            username = request_handler.get_current_user()
            WebSocketHandler.notify_username(username, e.message, "error")
            
        print response_data
        request_handler.finish(json.dumps(response_data))
    
