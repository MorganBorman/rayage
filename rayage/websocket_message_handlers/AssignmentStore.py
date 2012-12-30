from constants import *
import json

from DojoQuery import DojoQuery
from DojoSort import DojoSort

from ..WebSocketHandler import messageHandler
from ..DojoWebsocketJsonStoreHandler import DojoWebsocketJsonStoreHandler

from ..database.Assignment import Assignment
from ..database.SessionFactory import SessionFactory

@messageHandler("WebsocketJsonStore/Assignments", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class AssignmentStoreHandler(DojoWebsocketJsonStoreHandler):
    """
    Handles REST-like requests over the websocket for the lazy-loading editable table showing the assignments.
    """
    def __init__(self, message_type, required_fields, minimum_permission_level):
        DojoWebsocketJsonStoreHandler.__init__(self, message_type, required_fields, minimum_permission_level)
        
    def on_update(self, assignment_object):
        result_message = {'type': self.message_type,
                          'action': 'update',
                          'object': {'id': assignment_object.id, 'name': assignment_object.name, 'template': assignment_object.template, 'due_date': assignment_object.due_date},
                         }
        
        self.publish(json.dumps(result_message))
        
    def on_delete(self, object_id):
        result_message = {'type': self.message_type,
                          'action': 'delete',
                          'object': {'id': object_id},
                         }
        
        self.publish(json.dumps(result_message))
        
    def query(self, socket_connection, message, count, start, dojo_sort, dojo_query):
        session = SessionFactory()
        try:
            query = session.query(Assignment.id, Assignment.name, Assignment.template, Assignment.due_date)
        
            column_map = {u'id': Assignment.id, u'name': Assignment.name, u'template': Assignment.template, u'due_date': Assignment.due_date}
        
            if dojo_query:
                dojo_query_obj = DojoQuery(dojo_query)
                query = dojo_query_obj.apply_to_sqla_query(query, column_map)
                
            if dojo_sort is not None:
                dojo_sort_obj = DojoSort(dojo_sort)
                query = dojo_sort_obj.apply_to_sqla_query(query, column_map)
            
            assignment_count = query.count()
            assignment_list = query.offset(start).limit(count).all()
            assignment_list = [{'id': aid, 'name': name, 'template': template, 'due_date': due_date} for aid, name, template, due_date in assignment_list]
            
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
            
            self.on_update(assignment)
        finally:
            session.close()
            
        result_message = {'type': self.message_type,
                          'response': [],
                          'deferredId': message['deferredId'],
                         }
        
        socket_connection.write_message(json.dumps(result_message))
