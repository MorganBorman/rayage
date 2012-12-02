import logging
from SQLAlchemyHandler import SQLAlchemyHandler

# create logger
logger = logging.getLogger('rayage')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
#logger.addHandler(ch)

# create database handler and set level to debug
db = SQLAlchemyHandler()
db.setLevel(logging.DEBUG)

# add db handler to root logger
default_logger = logging.getLogger('')
default_logger.addHandler(db)
default_logger.addHandler(ch)
