import logging
import constants
from rayage.SQLAlchemyHandler import SQLAlchemyHandler

# create logger
logger = logging.getLogger('rayage')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(constants.CONSOLE_LOG_LEVEL)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# create database handler and set level to debug
db = SQLAlchemyHandler()
db.setLevel(constants.DATABASE_LOG_LEVEL)

# add ch and db handlers to root logger
default_logger = logging.getLogger('')
default_logger.addHandler(db)
default_logger.addHandler(ch)
