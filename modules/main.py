'''
Main module to run the entire pipeline
'''

from utils import get_airtable_data, send_push_notification, send_telegram_message
from utils import get_options_data, custom_logger
import datetime
from datetime import date
import dateutil
from venda_put_seco import venda_put_a_seco

logger = custom_logger()
logger.info('Inicio do processamento.')

# getting config params
configs = get_airtable_data('config')
configs = configs.set_index('key').T.to_dict()

# dates
today = date.today().strftime("%Y/%m/%d")
d_minus_1 = (dateutil.parser.parse(today) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
future_date = (dateutil.parser.parse(today) + datetime.timedelta(days=configs['NUM_MESES']['value']*30)).strftime('%Y-%m-%d')

# importing data
logger.info('Importando dados.')
try:
    #ticker_df = get_airtable_data('stocks_to_process')
    #ticker_list = ticker_df[ticker_df.process_options_strategy == True]['ticker'].to_list()
    ticker_list = ['VALE3', 'SUZB3']
    options_df = get_options_data(ticker_list, future_date)
    #print(options_df.head()) #REMOVE
    logger.info('Dados importados com sucesso.')
except:
    raise Exception('Falha ao importar os dados de opções.')

# strategies
try:
    v_put = venda_put_a_seco(options_df)
    print(v_put.head())
    logger.info('estratégia de venda de put a seco calculada com sucesso.')
except:
    raise Exception('Falha ao calcular estratégia de venda de put a seco.')



# add strategies decider

# push notifications
# send_push_notification("title", "message")
# send_telegram_message("test message")