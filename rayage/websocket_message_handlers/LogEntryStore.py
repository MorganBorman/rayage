from constants import *
import json

from DojoQuery import DojoQuery
from DojoSort import DojoSort

from ..WebSocketHandler import messageHandler
from ..RayageJsonStoreHandler import RayageJsonStoreHandler
from ..SQLAlchemyHandler import SQLAlchemyHandler

from ..database.LogEntry import LogEntry
from ..database.SessionFactory import SessionFactory

@messageHandler("RayageJsonStore/LogEntries", ['action', 'deferredId'], minimum_permission_level=PERMISSION_LEVEL_TA)
class LogEntryStoreHandler(RayageJsonStoreHandler):
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
