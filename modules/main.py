from utils import custom_logger, get_airtable_data, send_push_notification, send_telegram_message
from config import *

logger = custom_logger()
logger.info('This is a test')

print(PERC_CUTOFF)

# send_push_notification("title", "message")
# send_telegram_message("test message")
