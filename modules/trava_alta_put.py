"""
Module with functions to compute the strategy
"""
import pandas as pd


def trava_de_alta_com_put(trava_alta_put):
    """
    Function to compute the strategy of trava de alta com put
    """

    trava_alta_put["op_venc"] = pd.to_datetime(trava_alta_put["op_venc"], infer_datetime_format=True)
    trava_alta_put["ganho_max"] = trava_alta_put["upper_leg_vlr"] - trava_alta_put["lower_leg_vlr"]

    trava_alta_put["perda_max"] = (
        trava_alta_put["lower_leg_strike"]
        + trava_alta_put["upper_leg_vlr"]
        - trava_alta_put["upper_leg_strike"]
        - trava_alta_put["lower_leg_vlr"]
    )

    trava_alta_put["ganho_max_perc"] = abs(trava_alta_put["ganho_max"] / trava_alta_put["perda_max"])
    trava_alta_put["garantia_est"] = trava_alta_put["upper_leg_strike"] - trava_alta_put["lower_leg_strike"]
    trava_alta_put["razao"] = round(abs(trava_alta_put["perda_max"] / trava_alta_put["ganho_max"]))

    trava_alta_put = trava_alta_put[trava_alta_put.razao <= 5]
    trava_alta_put.sort_values(by=["ganho_max_perc", "prob_sucesso"], ascending=False, inplace=True)
    trava_alta_put.reset_index(drop=True, inplace=True)

    return trava_alta_put
