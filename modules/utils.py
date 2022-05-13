# module containing useful functions
import logging
from dotenv import load_dotenv
import pandas as pd
import os
import requests
from pushbullet import Pushbullet

load_dotenv('.env')

def custom_logger():
    '''
    Custom logging function
    '''
    LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    return logging.getLogger()
    
def get_airtable_data(table_name):
    '''
    Function to load managed data from airtable
    '''
    api_key = os.environ["AIRTABLE_API_KEY"]
    base_id = os.environ["AIRTABLE_BASE_ID"]
    url = "https://api.airtable.com/v0/" + base_id + "/" + table_name
    headers = {"Authorization": "Bearer " + api_key}
    
    # getting records
    response = requests.get(url, headers=headers)
    airtable_response = response.json()
    airtable_records = airtable_response['records']

    # parsing into a dict
    airtable_rows = [] 
    airtable_index = []
    for record in airtable_records:
        airtable_rows.append(record['fields'])
        airtable_index.append(record['id'])

    df = pd.DataFrame(airtable_rows, index=airtable_index).reset_index(drop=True)
    return df

def send_push_notification(title, message):
    '''
    Function to send push notifications through pushbullet
    '''
    api_key = os.environ["PUSHBULLET_API_KEY"]
    pb = Pushbullet(api_key)
    push = pb.push_note(title, message)

def send_telegram_message(message):
    '''
    Function to send automatic messages to a telegram channel
    '''
    bot = os.environ["TELEGRAM_BOT"]
    resp = requests.get(f'https://api.telegram.org/bot{bot}/getUpdates').json()
    try:
        chid = resp['result'][0]['message']['chat']['id']
    except:
        chid = int(os.environ["TELEGRAM_CHAT_ID"])
    pass

    send_text = 'https://api.telegram.org/bot' + bot + '/sendMessage'
    resp = requests.get(send_text, params={'chat_id': chid, 'parse_mode': 'Markdown', 'text': message})
    return resp.json()

def get_options_data():
    pass