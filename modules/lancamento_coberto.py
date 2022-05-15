'''
Module with functions to compute the strategy
'''
import pandas as pd
from datetime import date
from utils import get_airtable_data, get_stock_price

today = date.today().strftime("%Y/%m/%d")

def lancamento_coberto_acoes_em_custodia(df, num_negoc_min):
    '''
    Function to compute covered call strategy of stocks in custody
    '''
    # get stock average cost from airtable
    avg_price = get_airtable_data('avg_cost')
    tickers_avg_cost = {}

    for row in avg_price.iterrows():
        tickers_avg_cost[row[1]['ticker']] = row[1]['avg_price']

    # stock current price
    stock_current_price = {}
    for ticker in tickers_avg_cost.keys():
        stock_current_price[ticker]= round(get_stock_price(ticker), 2)

    l_coberto_carteira = df[df['acao'].isin(tickers_avg_cost.keys())]
    l_coberto_carteira['acao_pm'] = l_coberto_carteira['acao'].map(tickers_avg_cost)
    l_coberto_carteira['acao_strike_atual'] = l_coberto_carteira['acao'].map(stock_current_price)
    l_coberto_carteira['retorno_total'] = l_coberto_carteira['op_vlr'] + l_coberto_carteira['acao_strike_atual'] 

    l_coberto_carteira = l_coberto_carteira[['opcao', 'num_negoc', 'acao', 'acao_pm', 'acao_strike_atual','op_strike', 
                                            'op_vlr','op_venc', 'retorno_total']][(l_coberto_carteira.tipo=='CALL') \
                        & (l_coberto_carteira['op_venc'] > today) & (l_coberto_carteira['num_negoc'] >= num_negoc_min)]

    l_coberto_carteira['LP'] = l_coberto_carteira['retorno_total'] - l_coberto_carteira['acao_pm']
    l_coberto_carteira['LP_perc'] = ((l_coberto_carteira['retorno_total'] / l_coberto_carteira['acao_pm']) -1) *100

    l_coberto_carteira.sort_values(by=['acao', 'LP_perc'], ascending=False, inplace=True)

    l_coberto_carteira = l_coberto_carteira[(l_coberto_carteira.LP > 0)].reset_index(drop = True)

    return l_coberto_carteira
