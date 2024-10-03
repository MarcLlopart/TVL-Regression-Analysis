import streamlit as st
import pandas as pd
import plotly.graph_objs as go

from matplotlib.ticker import FuncFormatter

from utils import get_price, get_stables_mcap, get_staking_rewards, get_tvl, merge_df, get_staking_amounts
from utils import format_large_numbers

tvl_data = ['data/algorand.csv', 'data/aptos.csv', 'data/cardano.csv', 'data/icp.csv', 
            'data/near.csv', 'data/solana.csv', 'data/sui.csv', 'data/tezos.csv']

price_data = ['price/algo_usd.csv', 'price/apt_usd.csv', 'price/ada_usd.csv', 'price/icp_usd.csv',
              'price/near_usd.csv', 'price/sol_usd.csv', 'price/sui_usd.csv', 'price/xtz_usd.csv']

stables_data = ['algorand.csv', 'aptos.csv', 'cardano.csv', 'icp.csv', 
                'near.csv', 'solana.csv', 'sui.csv', 'tezos.csv']


staking_data = ['algorand.json', 'aptos.json', 'cardano.json', 'icp.json',
                'near.json', 'solana.json', 'sui.json',  'tezos.json']

chain_names = ['Algorand', 'Aptos', 'Cardano', 'ICP', 
               'NEAR', 'Solana', 'Sui', 'Tezos']

interest_rates = pd.read_csv('inlfation/interest_rates.csv',header=None)
interest_rates.drop(0, axis=1, inplace=True)
interest_rates.columns = ['Date', 'InterestRate']
interest_rates['Date'] = pd.to_datetime(interest_rates['Date'])

datasets = {}

for token in chain_names:
    file_idx = chain_names.index(token)
    tvl = get_tvl(token, tvl_data[file_idx])
    price = get_price(price_data[file_idx])
    stable = get_stables_mcap(stables_data[file_idx])
    staking = get_staking_rewards(staking_data[file_idx])
    stake_amount = get_staking_amounts(staking_data[file_idx])
    final_df = merge_df(tvl, price, stable, staking, stake_amount)
    final_df = final_df.merge(interest_rates, left_on='Date', right_on='Date', how='left')
    final_df.drop_duplicates(inplace=True)
    final_df.reset_index(inplace=True, drop=True)
    datasets[token] = final_df

# Streamlit app
st.title("Interactive Blockchain Data Plot")

# Dropdown menu to select the chain
chain_name = st.selectbox('Select a Blockchain:', list(datasets.keys()))

# Get the selected dataframe based on the chain
df = datasets[chain_name]

# Checkboxes for each line to be displayed
show_staking_rewards = st.checkbox('Show StakingRewards', value=True)
show_tvl = st.checkbox('Show TVL', value=True)
show_price = st.checkbox('Show Price', value=True)
show_staked_amount = st.checkbox('Show StakedAmount', value=True)

# Create the figure
fig = go.Figure()

# Track the number of selected variables for positioning
y_axis_count = 0

# Add traces to the figure for each selected line
if show_staking_rewards:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['StakingRewards'], mode='lines', name='StakingRewards',
                             line=dict(color='mediumblue', width=2),
                             yaxis='y1'))
    y_axis_count += 1

if show_tvl:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['TVL'], mode='lines', name='TVL',
                             line=dict(color='darkturquoise', width=2),
                             yaxis='y' + str(y_axis_count + 1)))
    y_axis_count += 1

if show_price:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['price'], mode='lines', name='Price',
                             line=dict(color='indigo', width=2),
                             yaxis='y' + str(y_axis_count + 1)))
    y_axis_count += 1

if show_staked_amount:
    fig.add_trace(go.Scatter(x=df['Date'], y=df['StakedAmount'], mode='lines', name='StakedAmount',
                             line=dict(color='purple', width=2),
                             yaxis='y' + str(y_axis_count + 1)))
    y_axis_count += 1

# Customize layout for multiple y-axes all on the left side with wider spacing
fig.update_layout(
    title=f'{chain_name} Data with Multiple Y-Axes',
    xaxis=dict(domain=[0.2,0.89]),
    yaxis=dict(
        title='StakingRewards',
        titlefont=dict(color='mediumblue'),
        tickfont=dict(color='mediumblue'),
        showgrid=False,  # No gridlines
        side='left',
        position=0.0,  # Position at the leftmost side
    ),
    # Dynamically create y-axes based on the number of selected traces
)

# Add remaining y-axes based on the selected variables
if show_tvl:
    fig['layout']['yaxis2'] = dict(
        title='TVL',
        titlefont=dict(color='darkturquoise'),
        tickfont=dict(color='darkturquoise'),
        overlaying='y',  # Overlay on the first axis
        side='left',
        anchor='free',   # Ensure it is free-floating
        position=0.15,  # Positioned slightly more to the right
        showgrid=False,
    )

if show_price:
    fig['layout']['yaxis3'] = dict(
        title='Price',
        titlefont=dict(color='indigo'),
        tickfont=dict(color='indigo'),
        overlaying='y',
        side='right',
        anchor='free',   # Ensure it is free-floating
        position=0.9,   # Further right to avoid overlap
        showgrid=False,
    )

if show_staked_amount:
    fig['layout']['yaxis4'] = dict(
        title='StakedAmount',
        titlefont=dict(color='purple'),
        tickfont=dict(color='purple'),
        overlaying='y',
        side='right',
        anchor='free',   # Ensure it is free-floating
        position=1,   # Further to the right of the third y-axis
        showgrid=False,
    )

# Set hover mode and legend
fig.update_layout(
    hovermode='x unified',  # To see hover info of all lines
    legend=dict(x=0, y=1.1, orientation='h')  # Horizontal legend
)

st.plotly_chart(fig)