'''
Module with functions to compute the strategy
'''
import pandas as pd
from datetime import date
from utils import get_airtable_data, get_stock_price

today = date.today().strftime("%Y/%m/%d")

# getting config params
configs = get_airtable_data('config')
configs = configs.set_index('key').T.to_dict()

def lancamento_coberto_acoes_em_custodia(df):
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
                        & (l_coberto_carteira['op_venc'] > today) & (l_coberto_carteira['num_negoc'] >= configs['NUM_NEGOC_MIN']['value'])]

    l_coberto_carteira['LP'] = l_coberto_carteira['retorno_total'] - l_coberto_carteira['acao_pm']
    l_coberto_carteira['LP_perc'] = ((l_coberto_carteira['retorno_total'] / l_coberto_carteira['acao_pm']) -1) *100

    l_coberto_carteira.sort_values(by=['acao', 'LP_perc'], ascending=False, inplace=True)

    l_coberto_carteira = l_coberto_carteira[(l_coberto_carteira.LP > 0)].reset_index(drop = True)

    return l_coberto_carteira

def lancamento_coberto_estrategia_OTM(df):
    '''
    Function to compute OTM covered call strategies
    '''
    l_coberto_OTM = df[['opcao', 'num_negoc', 'acao', 'acao_vlr', 'op_strike', 'op_vlr','op_venc']][(df.tipo=='CALL') \
                & (df['op_venc'] > today) & (df['num_negoc'] >= configs['NUM_NEGOC_MIN']['value'])]
    l_coberto_OTM['premio_perc'] = (l_coberto_OTM['op_vlr'] / l_coberto_OTM['acao_vlr']) *100
    l_coberto_OTM['strike_diff'] = l_coberto_OTM['op_strike'] - l_coberto_OTM['acao_vlr']

    l_coberto_OTM['lucro_venda'] = l_coberto_OTM['op_strike'] - l_coberto_OTM['acao_vlr']
    l_coberto_OTM['lucro_venda_perc'] = (l_coberto_OTM['op_strike'] / l_coberto_OTM['acao_vlr'] -1) *100
    l_coberto_OTM.sort_values(by='premio_perc', ascending=False, inplace=True)

    l_coberto_OTM = l_coberto_OTM[(l_coberto_OTM.strike_diff >= configs['LC_STRIKE_VLR_DIFF_LOWER']['value']) & \
                        (l_coberto_OTM.premio_perc > configs['PERC_CUTOFF']['value'])].reset_index(drop = True)
    return l_coberto_OTM

def lancamento_coberto_custo_final(df):
    '''
    Function to compute covered call strategy based on the final cost
    '''
    l_coberto = df[['opcao', 'num_negoc', 'acao', 'acao_vlr', 'op_strike', 'op_vlr','op_venc']][(df.tipo=='CALL') \
            & (df['op_venc'] > today) & (df['num_negoc'] >= configs['NUM_NEGOC_MIN']['value'])]
    l_coberto['custo_final'] = l_coberto['acao_vlr'] - l_coberto['op_vlr']
    l_coberto['premio_perc'] = (l_coberto['op_vlr'] / l_coberto['acao_vlr'])*100
    l_coberto['lucro_venda_acao'] = l_coberto['op_strike'] - l_coberto['custo_final']
    l_coberto['lucro_venda_acao_perc'] = (l_coberto['op_strike'] / l_coberto['custo_final'] -1)*100
    l_coberto['lucro_final_perc'] = ((l_coberto['op_vlr'] + l_coberto['lucro_venda_acao']) / l_coberto['acao_vlr'])*100

    l_coberto = l_coberto[(l_coberto.premio_perc >= configs['PERC_CUTOFF']['value']) & (l_coberto.lucro_venda_acao >0)]
    l_coberto.sort_values(by='premio_perc', ascending=False, inplace=True)
    return l_coberto
