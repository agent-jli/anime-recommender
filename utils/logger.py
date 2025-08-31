import logging
import os
from datetime import datetime
from config.config import LOG_TO_FILE

def get_logger(name, log_to_file=None):
    """
    Get logger with configurable output.
    
    Args:
        name: Logger name
        log_to_file: If True, log to file. If False, log to terminal. 
                    If None, uses LOG_TO_FILE environment variable (defaults to file)
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()
    
    logger.setLevel(logging.INFO)
    
    # Determine logging mode
    if log_to_file is None:
        # Check environment variable, default to file logging
        log_to_file = LOG_TO_FILE in ('true', '1', 'yes')
    
    # Configure handler based on preference
    if log_to_file:
        # File logging
        LOGS_DIR = "logs"
        os.makedirs(LOGS_DIR, exist_ok=True)
        LOG_FILE = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
        
        handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        # Terminal logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger