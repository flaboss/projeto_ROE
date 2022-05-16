'''
Script to test developed functions for CICD purposes
'''
import inspect
import datetime
from datetime import date
import dateutil
from modules.utils import get_airtable_data
from modules.utils import get_options_data, custom_logger
from modules.venda_put_seco import venda_put_a_seco

logger = custom_logger()
logger.info("Inicio do processamento de TESTE.")

# dates
today = date.today().strftime("%Y/%m/%d")
future_date = (
    dateutil.parser.parse(today)
    + datetime.timedelta(days=2 * 30)
).strftime("%Y-%m-%d")

# test functions
def test_airtable_retrieval():
    '''
    Function to test data retrieval from airtable.
    '''
    test_df = get_airtable_data("config")
    try:
        assert len(test_df) > 0
        logger.info(f'Teste da função {inspect.stack()[0][3]} passou.')
    except Exception:
        logger.error(f'Teste da função {inspect.stack()[0][3]} falhou.')
        
def test_get_options_data():
    '''
    Function to test option data retrieval.
    '''
    ticker_list=['PETR4', 'VALE3']
    test_df = get_options_data(ticker_list, future_date)
    try:
        assert len(test_df) > 0
        logger.info(f'Teste da função {inspect.stack()[0][3]} passou.')
        return test_df
    except Exception:
        logger.error(f'Teste da função {inspect.stack()[0][3]} falhou.')

def test_venda_put_a_seco(df):
    '''
    Function to test strategy venda de put a seco
    '''
    try:
        venda_put_a_seco(df)
        logger.info(f'Teste da função {inspect.stack()[0][3]} passou.')
    except Exception:
        logger.error(f'Teste da função {inspect.stack()[0][3]} falhou.')

if __name__ == '__main__':
    test_airtable_retrieval()
    test_data = test_get_options_data()
    test_venda_put_a_seco(test_data)
    