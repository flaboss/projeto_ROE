""" Module with functions to compute the strategy """
from datetime import date

import pandas as pd

from utils import get_airtable_data
from utils import stock_price_probability_given_distribution


today = date.today().strftime("%Y/%m/%d")
configs = get_airtable_data("config")
configs = configs.set_index("key").T.to_dict()


def venda_put_a_seco(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to compute strategy of selling puts
    """
    PERC_CUTOFF = configs["PERC_CUTOFF"]["value"]
    VP_STRIKE_VLR_DIFF_UPPER = configs["VP_STRIKE_VLR_DIFF_UPPER"]["value"]
    NUM_NEGOC_MIN = configs["NUM_NEGOC_MIN"]["value"]

    v_put = df[
        (df["tipo"] == "PUT")
        & (df["op_strike"] <= df["acao_vlr"])
        & (df["premio_perc"] > PERC_CUTOFF)
        & (df["op_venc"] > today)
        & (df["strike_diff"] <= VP_STRIKE_VLR_DIFF_UPPER)
        & (df["num_negoc"] >= NUM_NEGOC_MIN)
    ]
    v_put.sort_values(by="premio_perc", ascending=False, inplace=True)

    v_put["prob_acima"] = v_put.apply(stock_price_probability_given_distribution, axis=1)
    v_put["prob_acima"] = v_put["prob_acima"]
    v_put = v_put[
        [
            "opcao",
            "num_negoc",
            "acao",
            "acao_vlr",
            "op_strike",
            "op_vlr",
            "op_venc",
            "premio_perc",
            "strike_diff",
            "strike_perc",
            "prob_acima",
        ]
    ].reset_index(drop=True)

    return v_put
