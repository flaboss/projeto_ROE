# module containing useful functions
import logging

def custom_logger():
    LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logging.getLogger()
    
