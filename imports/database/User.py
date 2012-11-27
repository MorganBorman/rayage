from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, String

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

import time

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
    username = Column(String(64), nullable=False, unique=True)
    permission_level = Column(Integer)
    
    current_project = Column(String(64), nullable=True)
    user_since = Column(BigInteger, nullable=False)
    last_online = Column(BigInteger, nullable=False)

    @classmethod
    def get_user(cls, username):
        session = SessionFactory()
        try:
            user = session.query(User).filter_by(username=username).one()
            return user
        except NoResultFound:
            user = User(username)
            session.add(user)
            session.commit()
            print "Created new user entry in the database for user '{}'.".format(username)
        finally:
            session.close()
            
        # If the entry for the user was just created then retreive the committed version
        session = SessionFactory()
        try:
            user = session.query(User).filter_by(username=username).one()
            return user
        except NoResultFound:
            return None
        finally:
            session.close()
            
    def set_last_online(self, when):
        session = SessionFactory()
        try:
            user = session.query(User).filter_by(id=self.id).one()
            user.last_online = when
            session.add(user)
            session.commit()
        finally:
            session.close()
            
    def on_connect(self):
        self.set_last_online(0)
        
    def on_disconnect(self):
        self.set_last_online(int(time.time()))

    def __init__(self, username, permission_level=0):
        self.username = username
        self.permission_level = permission_level
        
        self.user_since = int(time.time())
        self.last_online = -1

    def __repr__(self):
        return "<User('%s', '%d')>" % (self.username, self.permission_level)
