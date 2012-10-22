from sqlalchemy import create_engine

engine = create_engine('sqlite:///rayage.db', echo=False)
