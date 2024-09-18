import numpy as np
import pandas as pd
import json


def format_large_numbers(x, pos):
    if np.abs(x) >= 1e9:
        return f'{x * 1e-9:.1f}B'  # Format as Billion
    elif np.abs(x) >= 1e6:
        return f'{x * 1e-6:.1f}M'  # Format as Million
    elif np.abs(x) >= 1e3:
        return f'{x * 1e-3:.1f}K'  # Format as Thousand
    else:
        return f'{x:.0f}'  # Less than 1,000
    
def get_tvl(chain : str , tvl_file : str):
    """
    Input: string and csv
    Output: dataframe with the defined format
    """
    df = pd.read_csv(tvl_file)

    protocol_name = df.columns[0]
    tvl_column = 'Total'

    #Transpose dates into rows 
    df_melted = df.melt(id_vars=[protocol_name], var_name='Date', value_name=chain)
    
    # Get the total TVL values
    df_melted = df_melted[df_melted[protocol_name]==tvl_column]

    df_melted['Date'] = pd.to_datetime(df_melted['Date'], format="%d/%m/%Y")
    df_melted = df_melted[df_melted['Date'] >= '01/01/2024']

    df_melted.reset_index(inplace=True, drop=True)
    df_melted = df_melted[['Date', chain]]

    return df_melted

def get_price(price_file: str):
    """
    Input: csv file with price feed from Coingecko
    Output: processed price df
    """
    price_df = pd.read_csv(price_file)
    price_df['snapped_at'] = pd.to_datetime(price_df['snapped_at'])
    price_df['snapped_at'] = price_df['snapped_at'].dt.strftime('%Y-%m-%d')
    price_df['snapped_at'] = pd.to_datetime(price_df['snapped_at'])
    return price_df

def get_stables_mcap(stablecoin_file: str):
    """ 
    Input: csv file with Stablecoins mcap from Defillama
    Output: processed df
    """
    stables = pd.read_csv(f'stablecoins/{stablecoin_file}')
    stables['Date'] = pd.to_datetime(stables['Date'])
    stables.rename(columns={'Total': 'StablesMCap'}, inplace=True)
    return stables[['Date', 'StablesMCap']]

def get_staking_rewards(staking_file : str):
    """ 
    Input: json file with staking metrics
    Output: Clean df with staking metrics
    """
    file_path = f'staking/{staking_file}'
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    
    metrics = json_data['data']['assets'][0]['metrics']
    df = pd.DataFrame(metrics)
    df['createdAt'] = df['createdAt'].str[:10]
    df.rename(columns={'defaultValue': 'StakingRewards'}, inplace=True)
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    return df

def merge_df(tvl_df : pd.DataFrame , price_df : pd.DataFrame, 
             stable_df: pd.DataFrame, staking_df: pd.DataFrame):
    """ 
    Input: 2 dataframes to merge
    Output: merged df with all info
    """

    merged_df = tvl_df.merge(price_df, left_on='Date', right_on='snapped_at', how='left')
    merged_df = merged_df.merge(stable_df, left_on='Date', right_on='Date', how='left')
    merged_df = merged_df.merge(staking_df, left_on='Date', right_on='createdAt', how='left')
    merged_df['Liquidity'] = merged_df['total_volume']/merged_df['market_cap'] * 100
    name = merged_df.columns[1]
    merged_df.rename(columns={name: 'TVL'}, inplace=True)
    merged_df.drop(['snapped_at', 'createdAt', 'metricKey'], axis=1, inplace=True)
    return merged_df