import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger('main')
logger.setLevel(logging.ERROR)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
log_handler = RotatingFileHandler('tululu.log', maxBytes=1024*1024, backupCount=2)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
