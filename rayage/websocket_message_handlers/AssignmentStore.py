from constants import *

import os
import json
import shutil
import os.path

from SimpleDojoQuery import SimpleDojoQuery
from DojoQuery import DojoQuery
from DojoSort import DojoSort

from ..WebSocketHandler import messageHandler
from ..DojoWebsocketJsonStoreHandler import DojoWebsocketJsonStoreHandler

from ..database.Assignment import Assignment
from ..database.SessionFactory import SessionFactory

def count_submissions(assignment_id):
    assignment_dir = os.path.join(ASSIGNMENTS_DIR, str(assignment_id))
    return len([name for name in os.listdir(assignment_dir) if os.path.isdir(os.path.join(assignment_dir, name))])

@messageHandler("WebsocketJsonStore/Assignments", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class AssignmentStoreHandler(DojoWebsocketJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the assignments.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        DojoWebsocketJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def object_to_json(self, assignment_object):
        return {'id': assignment_object.id, 
                'name': assignment_object.name, 
                'template': assignment_object.template, 
                'due_date': assignment_object.due_date,
                'submission_count': count_submissions(assignment_object.id)}
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(Assignment.id, Assignment.name, Assignment.template, Assignment.due_date)
        
            column_map = {u'id': Assignment.id, u'name': Assignment.name, u'template': Assignment.template, u'due_date': Assignment.due_date}
        
            if dojo_query:
                if u"op" in dojo_query.keys():
                    dojo_query_obj = DojoQuery(dojo_query)
                    query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                else:
                    dojo_query_obj = SimpleDojoQuery(dojo_query)
                    query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            assignment_count = query.count()
            assignment_list = query.offset(start).limit(count).all()
            assignment_list = map(self.object_to_json, assignment_list)
            
            result_message = {'type': self.message_type,
                              'response': assignment_list,
                              'total': assignment_count,
                              'deferredId': message['deferredId'],
                             }
        finally:
            session.close()
        
        socket_connection.write_message(json.dumps(result_message))
        
    def delete(self, socket_connection, message, object_id):
        
        if socket_connection.permission_level < PERMISSION_LEVEL_TA:
            raise InsufficientPermissions("You have insufficient permissions to modify or create assignments.")
            
        session = SessionFactory()
        try:
            assignment = session.query(Assignment).filter(Assignment.id==object_id).delete()
            session.commit()
        finally:
            session.close()
            
        assignment_dir = os.path.join(ASSIGNMENTS_DIR, str(object_id))
        if os.path.exists(assignment_dir):
            shutil.rmtree(assignment_dir)
            
        self.on_delete(object_id)
        
    def put(self, socket_connection, message, object_data):
            
        if socket_connection.permission_level < PERMISSION_LEVEL_TA:
            raise InsufficientPermissions("You have insufficient permissions to modify or create assignments.")
            
        session = SessionFactory()
        try:
            if object_data['id'] is not None:
                assignment = session.query(Assignment).filter(Assignment.id==int(object_data['id'])).one()
                assignment.name = object_data['name']
                assignment.template = object_data['template']
                assignment.due_date = object_data['due_date']
            else:
                assignment = Assignment(object_data['name'], object_data['template'], object_data['due_date'])
                
            session.add(assignment)
            session.commit()
            
            # Ensure the assignment turn in directory exists
            assignment_dir = os.path.join(ASSIGNMENTS_DIR, str(assignment.id))
            if not os.path.exists(assignment_dir):
                os.makedirs(assignment_dir)
            
            self.on_update(assignment)
        finally:
            session.close()
            
        result_message = {'type': self.message_type,
                          'response': self.object_to_json(assignment),
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
