import logging
import os
from logging.handlers import RotatingFileHandler

APP_LOGGER_NAME = 'log_rotation_system'

"""
This file sets up the main logging system for the log rotation project.
It creates a shared logger that writes messages to a log file and also
shows important warnings on the console. The rotating file handler keeps
the log from growing too large by creating backups automatically. Other
modules use this logger to record what’s happening while the program runs.
"""

def init(log_file_path='./app.log', log_level=logging.INFO):
    
    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger
    
    log_directory = os.path.dirname(log_file_path)
    if log_directory and not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10*1024*1024,  
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Logger initialized successfully")
    return logger

def get_logger():
    logger = logging.getLogger(APP_LOGGER_NAME)
    if not logger.handlers:
        return init() 
    return logger
