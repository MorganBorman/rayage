from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, String

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
    username = Column(String(64), nullable=False, unique=True)
    permission_level = Column(Integer)

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

    def __init__(self, username, permission_level=0):
        self.username = username
        self.permission_level = permission_level

    def __repr__(self):
        return "<User('%s', '%d')>" % (self.username, self.permission_level)
