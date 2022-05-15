'''
Module with functions to compute the strategy
'''
import pandas as pd

def capital_garantido(df_cap_garantido):
    '''
    Funtion for computing strategy capital garantido
    '''
    df_cap_garantido['op_venc'] = pd.to_datetime(df_cap_garantido['op_venc'],infer_datetime_format=True)
    df_cap_garantido['credito_operacao'] = df_cap_garantido.call_premio - df_cap_garantido.put_premio
    df_cap_garantido['lucro_max'] = df_cap_garantido.call_strike - df_cap_garantido.acao_vlr + df_cap_garantido.credito_operacao
    df_cap_garantido['custo_total'] = df_cap_garantido.call_premio - df_cap_garantido.acao_vlr - df_cap_garantido.put_premio
    df_cap_garantido['lucro_max_perc'] = abs(df_cap_garantido.lucro_max/df_cap_garantido.custo_total)*100
    df_cap_garantido['credito_perc'] = abs(df_cap_garantido.credito_operacao/df_cap_garantido.custo_total)*100
    df_cap_garantido = df_cap_garantido[df_cap_garantido.credito_perc > 1]
    df_cap_garantido.sort_values(by='credito_perc', ascending=False, inplace=True)
    df_cap_garantido.reset_index(drop=True, inplace=True)
    
    return df_cap_garantido