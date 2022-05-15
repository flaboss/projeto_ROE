'''
Main module to run the entire pipeline
'''

from utils import get_airtable_data, send_push_notification, send_telegram_message
from utils import get_options_data, custom_logger, push_df_to_datapane_reports
import datetime
from datetime import date
import dateutil
from pandasql import sqldf
from venda_put_seco import venda_put_a_seco
from trava_alta_put import trava_de_alta_com_put
from capital_garantido import capital_garantido
from lancamento_coberto import lancamento_coberto_acoes_em_custodia, lancamento_coberto_estrategia_OTM
from lancamento_coberto import lancamento_coberto_custo_final

logger = custom_logger()
logger.info('Inicio do processamento.')

# getting config params
configs = get_airtable_data('config')
configs = configs.set_index('key').T.to_dict()

# getting deciders
deciders = get_airtable_data('deciders')
deciders = deciders.set_index('key').T.to_dict()

# dates
today = date.today().strftime("%Y/%m/%d")
d_minus_1 = (dateutil.parser.parse(today) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
future_date = (dateutil.parser.parse(today) + datetime.timedelta(days=configs['NUM_MESES']['value']*30)).strftime('%Y-%m-%d')


###
# IMPORTING DATA
###

logger.info('Importando dados.')
try:
    #ticker_df = get_airtable_data('stocks_to_process')
    #ticker_list = ticker_df[ticker_df.process_options_strategy == True]['ticker'].to_list()
    ticker_list = ['VALE3', 'SUZB3']
    options_df = get_options_data(ticker_list, future_date)
    #print(options_df.head()) #REMOVE
    logger.info('Dados importados com sucesso.')
except:
    send_push_notification("Estratégia de opções", "Falha ao importar dados de opções")
    raise Exception('Falha ao importar os dados de opções.')

###
# STRATEGIES
###

# venda de put
if deciders['VENDA_PUT_DECIDER']['value'] == True:
    logger.info('Iniciando execução de estratégia de venda de put a seco.')
    try:
        v_put = venda_put_a_seco(options_df)
        logger.info('estratégia de venda de put a seco calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de venda de put")
        raise Exception('Falha ao calcular estratégia de venda de put a seco.')
else:
    v_put = None
    logger.warning('Estratégia de venda de put a seco não será executada.')

# trava de alta com put
if deciders['TRAVA_ALTA_PUT_DECIDER']['value'] == True:
    logger.info('Iniciando execução de estratégia de trava de alta com put.')

    # check if v_put exists
    if v_put is None:
        v_put = venda_put_a_seco(options_df)

    # create a self joined table
    pysqldf = lambda q: sqldf(q, globals())
    query = """
    select upper.acao, upper.acao_vlr, upper.op_venc, upper.opcao as upper_leg_opcao, upper.op_strike as upper_leg_strike, 
        upper.op_vlr as upper_leg_vlr, lower.opcao as lower_leg_opcao, lower.op_strike as lower_leg_strike, 
        lower.op_vlr as lower_leg_vlr, upper.prob_acima as prob_sucesso
    from v_put upper
    inner join v_put lower
        on upper.acao = lower.acao and upper.op_vlr > lower.op_vlr and upper.op_venc = lower.op_venc;
    """
    self_join_df = pysqldf(query)

    try:
        ta_put = trava_de_alta_com_put(self_join_df)
        
        logger.info('estratégia de trava de alta com put calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de trava de alta com put.")
        raise Exception('Falha ao calcular estratégia trava de alta com put.')
else:
    logger.warning('Estratégia de trava de alta com put não será executada.')

# capital garantido 
if deciders['CAPITAL_GARANTIDO_DECIDER']['value'] == True:
    try:
        logger.info('Iniciando execução de estratégia de trava de capital garantido.')

        PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO = configs['PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO']['value']
        
        df_cap_garantido_strikes = options_df[(options_df.op_strike >= options_df.acao_vlr - (options_df.acao_vlr \
            * PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO))
            & (options_df.op_strike <= options_df.acao_vlr * (1+PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO))]

        pysqldf = lambda q: sqldf(q, globals())
        query = """
        with put as (
            select * 
            from df_cap_garantido_strikes
            where tipo = 'PUT'
        ),

        call as (
            select * 
            from df_cap_garantido_strikes
            where tipo = 'CALL'
        )

        select call.acao, call.op_venc, call.acao_vlr, call.opcao as venda_call, call.op_strike as call_strike,
            call.op_vlr as call_premio, put.opcao as compra_put, put.op_strike as put_strike, put.op_vlr as put_premio
        from call
        inner join put
            on call.acao = put.acao and call.op_venc = put.op_venc
        """

        df_cap_garantido = pysqldf(query)
        df_cap_garantido = capital_garantido(df_cap_garantido)

        logger.info('estratégia de capital garantido calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de capital garantido.")
        raise Exception('Falha ao calcular estratégia de capital garantido.')
else:
    logger.warning('Estratégia de capital garantido não será executada.')

# lancamento coberto para acoes em custodia
if deciders['LANC_COBERTO_ACOES_CARTEIRA']['value'] == True:
    try:
        logger.info('Iniciando execução de estratégia de lançamento coberto de ações em custodia.')
        l_coberto_custodia = lancamento_coberto_acoes_em_custodia(options_df)
        logger.info('estratégia de lançamento coberto de ações em custódia calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de lancamento coberto para acoes em custodia.")
        raise Exception('Falha ao calcular estratégia lancamento coberto para acoes em custodia.')
else:
    logger.warning('Estratégia de lançamento coberto de ações em custódia não será executada.')

# lancamento coberto estrategia OTM
if deciders['LANC_COBERTO_OTM']['value'] == True:
    try:
        logger.info('Iniciando execução de estratégia de lançamento coberto OTM.')
        l_coberto_OTM = lancamento_coberto_estrategia_OTM(options_df)
        logger.info('estratégia de lançamento coberto OTM calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de lancamento coberto OTM.")
        raise Exception('Falha ao calcular estratégia lancamento coberto OTM.')
else:
    logger.warning('Estratégia de lançamento coberto OTM não será executada.')

# lancamento coberto custo final
if deciders['LANC_COBERTO_CUSTO_FINAL']['value'] == True:
    try:
        logger.info('Iniciando execução de estratégia de lançamento coberto baseada no custo final.')
        l_coberto_custo_final = lancamento_coberto_custo_final(options_df)
        logger.info('estratégia de lançamento coberto (custo final) calculada com sucesso.')
    except:
        send_push_notification("Estratégia de opções", "Falha ao executar estratégia de lancamento coberto (custo final).")
        raise Exception('Falha ao calcular estratégia lancamento coberto (custo final).')
else:
    logger.warning('Estratégia de lançamento coberto (custo final) não será executada.')

###
# REPORT
###
#push_df_to_datapane_reports(v_put, 'Estrategias de Opções')

###
# NOTIFICATIONS
###
# send_push_notification("title", "message")
# send_telegram_message("test message")