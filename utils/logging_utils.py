import os
import logging
from datetime import datetime

def setup_logging(log_dir: str, log_file_prefix: str):
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = f"{log_file_prefix}_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    logger_name = f"custom_logger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger
