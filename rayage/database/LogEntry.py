from sqlalchemy import Column, Sequence
from sqlalchemy.types import DateTime, Integer, String

from sqlalchemy.sql import func

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

# Based on the schema described in the following post;
# http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/logging/sqlalchemy_logger.html

class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, Sequence('log_entries_id_seq'), primary_key=True)
    timestamp = Column(DateTime, default=func.now()) # the current timestamp
    logger = Column(String(64)) # the name of the logger. (e.g. myapp.views)
    level = Column(Integer) # info, debug, or error?
    trace = Column(String(512)) # the full traceback printout
    msg = Column(String(512)) # custom log info

    def __init__(self, logger=None, level=None, trace=None, msg=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg

    def __repr__(self):
        return "<LogEntry('%s', '%d')>" % (self.username, self.permission_level)
