# Based on the system described in the following post;
# http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/logging/sqlalchemy_logger.html

import logging
import traceback
from SignalObject import Signal

from database.LogEntry import LogEntry
from database.SessionFactory import SessionFactory

class SQLAlchemyHandler(logging.Handler):
    RecordEmitted = Signal()
    
    def __init__(self):
        logging.Handler.__init__(self)
    
    # A very basic logger that commits LogEntry records to the database
    def emit(self, record):
        trace = None
        exc = record.__dict__['exc_info']
        
        if exc:
            trace = traceback.format_exc(exc)
        
        session = SessionFactory()
        try:
            log_entry = LogEntry(logger=record.__dict__['name'],
                                 level=record.__dict__['levelno'],
                                 trace=trace,
                                 msg=(record.msg % record.args),)
                        
            session.add(log_entry)
            
            session.flush()
            session.refresh(log_entry)
            
            self.RecordEmitted.emit(log_entry)
            
            session.commit()
        finally:
            session.close()
            
