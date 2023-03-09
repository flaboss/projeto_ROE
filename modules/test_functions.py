""" Script to test developed functions for CICD purposes """
import datetime
import inspect
from datetime import date

import dateutil
from utils import custom_logger
from utils import get_options_data


logger = custom_logger()
logger.info("Inicio do processamento de TESTE.")

# dates
today = date.today().strftime("%Y/%m/%d")
future_date = (dateutil.parser.parse(today) + datetime.timedelta(days=2 * 30)).strftime("%Y-%m-%d")


# test functions
def test_get_options_data():
    """
    Function to test option data retrieval.
    """
    ticker_list = ["PETR4", "VALE3"]
    test_df = get_options_data(ticker_list, future_date)
    try:
        assert len(test_df) > 0
        logger.info(f"Teste da função {inspect.stack()[0][3]} passou.")
        return test_df
    except Exception:
        logger.error(f"Teste da função {inspect.stack()[0][3]} falhou.")


if __name__ == "__main__":
    test_data = test_get_options_data()
