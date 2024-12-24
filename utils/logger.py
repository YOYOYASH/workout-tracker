import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_dir='user_logs', log_file='app.log', level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # More verbose for console
    stream_formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    stream_handler.setFormatter(stream_formatter)
    
    # File Handler with Rotation
    file_path = os.path.join(log_dir, log_file)
    file_handler = RotatingFileHandler(
        file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)  # Less verbose for files
    file_formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    file_handler.setFormatter(file_formatter)
    
    # Adding Handlers
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger