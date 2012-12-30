from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, String

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, Sequence('assignments_id_seq'), primary_key=True)
    name = Column(String(64), nullable=False, unique=False)
    
    template = Column(String(64), nullable=False, unique=False)
    
    due_date = Column(BigInteger, nullable=False)

    def __init__(self, name, template, due_date):
        self.template = template
        self.name = name
        self.due_date = due_date

    def __repr__(self):
        return "<Assignment('%s', '%s', %d)>" % (self.template, self.name, self.due_date)
