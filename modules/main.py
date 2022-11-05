"""
Main module to run the entire pipeline
"""

from utils import get_airtable_data, send_push_notification, send_telegram_message
from utils import (
    get_options_data,
    custom_logger,
    push_df_to_datapane_reports,
    upload_data_bitdotio,
    get_tickers_to_be_processed
)
import datetime
from datetime import date
import dateutil
from pandasql import sqldf
from venda_put_seco import venda_put_a_seco
from trava_alta_put import trava_de_alta_com_put
from capital_garantido import capital_garantido
from lancamento_coberto import (
    lancamento_coberto_acoes_em_custodia,
    lancamento_coberto_estrategia_OTM,
)
from lancamento_coberto import lancamento_coberto_custo_final

logger = custom_logger()
logger.info("Inicio do processamento.")

# getting config params
configs = get_airtable_data("config")
configs = configs.set_index("key").T.to_dict()

# getting deciders
deciders = get_airtable_data("deciders")
deciders = deciders.set_index("key").T.to_dict()

# dates
today = date.today().strftime("%Y/%m/%d")
d_minus_1 = (dateutil.parser.parse(today) - datetime.timedelta(days=1)).strftime(
    "%Y-%m-%d"
)
future_date = (
    dateutil.parser.parse(today)
    + datetime.timedelta(days=configs["NUM_MESES"]["value"] * 30)
).strftime("%Y-%m-%d")

# data frames for datapane report
dfs_to_report = {}

# qty of days to keep in bit.io
qty_days_to_keep = configs["QT_DAYS_KEEP_DATA"]["value"]

###
# IMPORTING DATA
###

logger.info("Importando dados.")
try:
    ticker_df = get_airtable_data("stocks_to_process")
    ticker_df.fillna(False, inplace=True)
    ticker_df['process'] = ticker_df.sum(axis=1)

    ticker_list = ticker_df[ticker_df.process > 0][
        "ticker"
    ].to_list()

    options_df = get_options_data(ticker_list, future_date)
    logger.info("Dados importados com sucesso.")
except Exception:
    send_push_notification("Estratégia de opções", "Falha ao importar dados de opções")
    raise Exception("Falha ao importar os dados de opções.")

###
# STRATEGIES
###

# venda de put a seco
if deciders["VENDA_PUT_DECIDER"]["value"] is True:
    logger.info("Iniciando execução de estratégia de venda de put a seco.")
    try:
        v_put = venda_put_a_seco(options_df[options_df['acao'].isin(get_tickers_to_be_processed('process_v_put_seco'))])
        dfs_to_report["## Venda de put a seco"] = v_put
        upload_data_bitdotio(v_put, "estr_venda_put_seco", today, qty_days_to_keep)

        logger.info("estratégia de venda de put a seco calculada com sucesso.")
    except Exception:
        send_push_notification(
            "Estratégia de opções", "Falha ao executar estratégia de venda de put"
        )
        raise Exception("Falha ao calcular estratégia de venda de put a seco.")
else:
    v_put = None
    logger.warning("Estratégia de venda de put a seco não será executada.")

# trava de alta com put
if deciders["TRAVA_ALTA_PUT_DECIDER"]["value"] is True:
    logger.info("Iniciando execução de estratégia de trava de alta com put.")

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
        df_to_process = self_join_df[self_join_df['acao'].isin(get_tickers_to_be_processed('process_trava_alta_put'))]
        ta_put = trava_de_alta_com_put(df_to_process)
        dfs_to_report["## Trava de Alta com Put"] = ta_put
        upload_data_bitdotio(ta_put, "estr_trava_alta_put", today, qty_days_to_keep)

        logger.info("estratégia de trava de alta com put calculada com sucesso.")
    except Exception:
        send_push_notification(
            "Estratégia de opções",
            "Falha ao executar estratégia de trava de alta com put.",
        )
        raise Exception("Falha ao calcular estratégia trava de alta com put.")
else:
    logger.warning("Estratégia de trava de alta com put não será executada.")

# capital garantido
if deciders["CAPITAL_GARANTIDO_DECIDER"]["value"] is True:
    try:
        logger.info("Iniciando execução de estratégia de trava de capital garantido.")

        PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO = configs[
            "PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO"
        ]["value"]

        df_cap_garantido_strikes = options_df[
            (
                options_df.op_strike
                >= options_df.acao_vlr
                - (options_df.acao_vlr * PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO)
            )
            & (
                options_df.op_strike
                <= options_df.acao_vlr * (1 + PERC_STRIKE_DIF_PARA_CAPITAL_GARANTIDO)
            )
        ]

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
        df_to_process = df_cap_garantido[df_cap_garantido['acao'].isin(get_tickers_to_be_processed('process_capital_garantido'))]
        df_cap_garantido = capital_garantido(df_to_process)
        dfs_to_report["## Capital Garantido"] = df_cap_garantido
        upload_data_bitdotio(
            df_cap_garantido, "estr_capital_garantido", today, qty_days_to_keep
        )

        logger.info("estratégia de capital garantido calculada com sucesso.")
    except Exception:
        send_push_notification(
            "Estratégia de opções", "Falha ao executar estratégia de capital garantido."
        )
        raise Exception("Falha ao calcular estratégia de capital garantido.")
else:
    logger.warning("Estratégia de capital garantido não será executada.")

# lancamento coberto para acoes em custodia
if deciders["LANC_COBERTO_ACOES_CARTEIRA"]["value"] is True:
    try:
        logger.info(
            "Iniciando execução de estratégia de lançamento coberto de ações em custodia."
        )
        # acoes em custodia ja definidas na aba avg_cost do airtable
        l_coberto_custodia = lancamento_coberto_acoes_em_custodia(options_df)
        dfs_to_report["## Lançamento Coberto de Ações em Custódia"] = l_coberto_custodia
        upload_data_bitdotio(
            l_coberto_custodia,
            "estr_lancamento_coberto_custodia",
            today,
            qty_days_to_keep,
        )

        logger.info(
            "estratégia de lançamento coberto de ações em custódia calculada com sucesso."
        )
    except Exception:
        send_push_notification(
            "Estratégia de opções",
            "Falha ao executar estratégia de lancamento coberto para acoes em custodia.",
        )
        raise Exception(
            "Falha ao calcular estratégia lancamento coberto para acoes em custodia."
        )
else:
    logger.warning(
        "Estratégia de lançamento coberto de ações em custódia não será executada."
    )

# lancamento coberto estrategia OTM
if deciders["LANC_COBERTO_OTM"]["value"] is True:
    try:
        logger.info("Iniciando execução de estratégia de lançamento coberto OTM.")
        df_to_process = options_df[options_df['acao'].isin(get_tickers_to_be_processed('process_l_coberto_otm'))]
        l_coberto_OTM = lancamento_coberto_estrategia_OTM(df_to_process)
        dfs_to_report["## Lançamento Coberto (estratégia OTM)"] = l_coberto_OTM
        upload_data_bitdotio(
            l_coberto_OTM, "estr_lancamento_coberto_otm", today, qty_days_to_keep
        )

        logger.info("estratégia de lançamento coberto OTM calculada com sucesso.")
    except Exception:
        send_push_notification(
            "Estratégia de opções",
            "Falha ao executar estratégia de lancamento coberto OTM.",
        )
        raise Exception("Falha ao calcular estratégia lancamento coberto OTM.")
else:
    logger.warning("Estratégia de lançamento coberto OTM não será executada.")

# lancamento coberto custo final
if deciders["LANC_COBERTO_CUSTO_FINAL"]["value"] is True:
    try:
        logger.info(
            "Iniciando execução de estratégia de lançamento coberto baseada no custo final."
        )
        df_to_process = options_df[options_df['acao'].isin(get_tickers_to_be_processed('process_l_coberto_custo_final'))]
        l_coberto_custo_final = lancamento_coberto_custo_final(df_to_process)
        dfs_to_report["## Lançamento Coberto (custo final)"] = l_coberto_custo_final
        upload_data_bitdotio(
            l_coberto_custo_final,
            "estr_lancamento_coberto_custo_final",
            today,
            qty_days_to_keep,
        )

        logger.info(
            "estratégia de lançamento coberto (custo final) calculada com sucesso."
        )
    except Exception:
        send_push_notification(
            "Estratégia de opções",
            "Falha ao executar estratégia de lancamento coberto (custo final).",
        )
        raise Exception(
            "Falha ao calcular estratégia lancamento coberto (custo final)."
        )
else:
    logger.warning("Estratégia de lançamento coberto (custo final) não será executada.")

###
# REPORT
###

push_df_to_datapane_reports(dfs_to_report, "Estrategias de Opções")

###
# NOTIFICATIONS
###

title = "Estratégia de opções"
message = "Estratégias de Opções Executada com sucesso! https://datapane.com/reports/E7ywxlA/estrategias-de-op%C3%A7%C3%B5es/"

if deciders["SEND_PUSH_NOTIFICATION"]["value"] is True:
    send_push_notification(title, message)

if deciders["SEND_TELEGRAM_NOTIFICATION"]["value"] is True:
    send_telegram_message(message)
