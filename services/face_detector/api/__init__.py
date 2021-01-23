
import os
import logging
from logging import StreamHandler
from logging import FileHandler
from api.config import config


env = os.getenv('FLASK_ENV')
log_file = config[env].LOG_FILE

# Create the Logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create the Handler for logging data to a file
logger_handler = FileHandler(log_file)
logger_handler.setLevel(logging.INFO)

#Create the Handler for logging data to console.
console_handler = StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(filename)s %(funcName)s %(lineno)d: %(message)s')
# logger_formatter = logging.Formatter("%(asctime)s: %(levelname)s in [%(module)s: %(lineno)d]: %(message)s")

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)
console_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
root_logger.addHandler(logger_handler)
root_logger.addHandler(console_handler)