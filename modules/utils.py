# module containing useful functions
import logging
from dotenv import load_dotenv
import pandas as pd
import os
import requests
from pushbullet import Pushbullet
from pandas_datareader import data as web
from datetime import date
import datetime
from scipy.stats import norm
import datapane as dp

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

def get_stock_price(ticker):
    '''
    Function to fetch stock last price from yahoo finance
    '''
    return web.get_data_yahoo(f'{ticker}.sa')[-1:].Close[0]

def list_stock_options_by_exp_date(ticker, exp_date):
    '''
    Lists all stock options given an expiration date
    '''
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={ticker}&listarVencimentos=False&cotacoes=true&vencimentos={exp_date}'
    r = requests.get(url).json()
    data = [[ticker, exp_date, i[0].split('_')[0], i[2], i[3],  i[5], i[8], i[9]] for i in r['data']['cotacoesOpcoes']]
    return pd.DataFrame(data, columns=['acao', 'op_venc', 'opcao', 'tipo', 'modelo', 'op_strike', 'op_vlr', 'num_negoc'])

def list_stock_options(ticker, future_dt):
    '''
    Fetches all stock options until a defined future date
    '''
    url= f'https://opcoes.net.br/listaopcoes/completa?idAcao={ticker}&listarVencimentos=true&cotacoes=true'
    r = requests.get(url).json()
    vencimentos = [i['value'] for i in r['data']['vencimentos'] if i['value'] <= future_dt]
    data =  pd.concat([list_stock_options_by_exp_date(ticker, vencimento) for vencimento in vencimentos])
    return data.dropna()

def get_options_data(ticker_list, future_dt):
    options = []
    logger = custom_logger()

    for ticker in ticker_list:
        try:
            stock_price = get_stock_price(ticker)
            options_data = list_stock_options(ticker, future_dt)
            options_data['acao_vlr'] = stock_price
            options.append(options_data.values.tolist())
        except:
            send_telegram_message(f'Falha ao importar dados de {ticker}')
            logger.error(f'Falha ao importar dados de {ticker}')
            pass

    df_options = pd.concat(pd.DataFrame(i) for i in options)
    df_options.columns = ['acao', 'op_venc', 'opcao', 'tipo', 'modelo', 'op_strike', 'op_vlr', 'num_negoc', 'acao_vlr']

    # new columns
    df_options['premio_perc'] = (df_options['op_vlr'] / df_options['op_strike']) *100
    df_options['strike_diff'] = df_options['op_strike'] - df_options['acao_vlr']
    df_options['strike_perc'] = ((df_options['op_strike'] / df_options['acao_vlr']) -1) *100
    df_options['op_venc'] = pd.to_datetime(df_options['op_venc'],infer_datetime_format=True)
    
    return df_options

def stock_price_probability_given_distribution(row):
    '''
    Computes the probability of a stock price being above a threshold given past data distribution.
    '''
    configs = get_airtable_data('config')
    configs = configs.set_index('key').T.to_dict()
    lookback = configs['DATA_LOOKBACK_YEARS']['value']
    
    try:
        diff = (row.op_venc - pd.to_datetime(date.today())).days
        ticker = row.acao
        strike = row.op_strike
        vlr_acao = row.acao_vlr
        dt_inic = (date.today() + datetime.timedelta(weeks=-52*lookback))
        tmp_df = web.get_data_yahoo(f'{ticker}.sa', dt_inic, date.today())
        tmp_df['close_shifted'] = tmp_df['Close'].shift(periods = diff)
        tmp_df['return'] = tmp_df['Close']/tmp_df['close_shifted'] -1
        desv = tmp_df['return'].std()
        media = tmp_df['return'].mean()
        return_periodo = strike/vlr_acao-1
        z = (return_periodo - media)/desv
        prob_acima = round(1-norm.cdf(z),2)
    except:
        raise Exception('Falha ao computar probabilidade de preço da ação.')

    return prob_acima

def push_df_to_datapane_reports(dataframes, report_name):
    api_key = os.environ["DATAPANE_API_KEY"]
    os.system(f'!datapane login --{api_key}')

    dp.Report(
        dp.DataTable(dataframes)
    ).upload(name=report_name)