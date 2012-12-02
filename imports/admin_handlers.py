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
from database.LogEntry import LogEntry
from database.SessionFactory import SessionFactory

from SQLAlchemyHandler import SQLAlchemyHandler

from DojoQuery import DojoQuery
from DojoSort import DojoSort

admin_modules = [
    { 'id': 'admin_modules', 'name': 'Admin Modules', 'type':'folder', 'iconClass': 'modules'},
    { 'id': 'view_statistics', 'name': 'View Statistics', 'type': 'custom/StatisticsViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'view_statistics'},
    { 'id': 'user_manager', 'name': 'Manage Users', 'type': 'custom/UserManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'users'},
    { 'id': 'template_manager', 'name': 'Manage Templates', 'type': 'custom/TemplateManager', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'templates'},
    { 'id': 'log_viewer', 'name': 'View Logs', 'type': 'custom/LogViewer', 'parent': 'admin_modules', 'params': {}, 'iconClass': 'logs'},
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
        """
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
        """
        
    def on_update(self, user_object):
        result_message = {'type': "RayageJsonStore/Users",
                          'action': 'update',
                          'object': {'id': user_object.id, 'username': user_object.username, 'permissions': user_object.permission_level},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(User.id, User.username, User.permission_level, User.user_since, User.last_online)
        
            column_map = {u'id': User.id, u'username': User.username, u'permissions': User.permission_level}
        
            if dojo_query:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            user_count = query.count()
            user_list = query.offset(start).limit(count).all()
            user_list = [{'id': uid, 'username': username, 'permissions': permission_level, 'user_since': user_since, 'last_online': last_online} for uid, username, permission_level, user_since, last_online in user_list]
            
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
            
            self.on_update(user)
            
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
        
@messageHandler("RayageJsonStore/LogEntries", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class UserStoreHandler(RayageJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the log entries.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        RayageJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
        SQLAlchemyHandler.RecordEmitted.connect(self.on_new_record)
        
    def on_new_record(self, log_entry):
        result_message = {'type': "RayageJsonStore/LogEntries",
                          'action': 'update',
                          'object': {u'id': log_entry.id, u'timestamp': log_entry.timestamp.isoformat(), u'logger': log_entry.logger, 
                                     u'level': log_entry.level, u'trace': log_entry.trace, u'message': log_entry.msg},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
        
            column_map = {u'id': LogEntry.id, u'timestamp': LogEntry.timestamp, u'logger': LogEntry.logger, u'level': LogEntry.level, u'trace': LogEntry.trace, u'message': LogEntry.msg}
            
            query = session.query(LogEntry.id, LogEntry.timestamp, LogEntry.logger, LogEntry.level, LogEntry.trace, LogEntry.msg)
            
            if dojo_query:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            log_entry_count = query.count()
            log_entry_list = query.offset(start).limit(count).all()
            log_entry_list = [{u'id': id, u'timestamp': timestamp.isoformat(), u'logger': logger, u'level': level, u'trace': trace, u'message': msg}
                                for id, timestamp, logger, level, trace, msg in log_entry_list]
            
            result_message = {'type': message[u'type'],
                              'response': log_entry_list,
                              'total': log_entry_count,
                              'deferredId': message['deferredId'],
                             }
        finally:
            session.close()
        
        socket_connection.write_message(json.dumps(result_message))
    
