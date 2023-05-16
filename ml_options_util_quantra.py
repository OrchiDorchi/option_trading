import numpy as np
import pandas as pd
from scipy.stats import rv_histogram
from scipy.stats import lognorm


def get_premium(options_strategy, options_data):
    strike = options_strategy['Strike Price']
    option_type = options_strategy['Option Type']

    if option_type == 'CALL':
        return options_data[options_data['STRIKE'] == strike].C_LAST
    if option_type == 'PUT':
        return options_data[options_data['STRIKE'] == strike].P_LAST
    return 0

def advice():
    options_data = pd.read_pickle(
    'spx_eom_expiry_options_2010_2022.bz2')
    options_data.columns = options_data.columns.str.replace(
        "[", "").str.replace("]", "").str.strip()
    data = pd.read_csv('spy_signals_2018_2022.csv', index_col=0)
    spx = pd.read_csv('spx.csv', index_col=0)
    data['signal'] = data['predicted_signal']
    start_date = data.index[0]
    last_day = data.loc[start_date:].index.to_list()[-1]
    options_data_daily = options_data.loc[last_day]
    spread = setup_call_spread(options_data_daily, 10)
    spread['position'] = np.where(spread['position'] > 0, 'LONG', 'SHORT')
    spread['expiration'] = '30d'
    spread = spread[['position','Option Type','Strike Price','premium','expiration']]
    return spx.loc[last_day]['Adj Close'],spread
def setup_call_spread(options_data, strike_difference=10):
    if options_data is None:
        pass
    call_spread = pd.DataFrame(columns=['Option Type', 'Strike Price', 'position', 'premium'])

    underlying_price = options_data['UNDERLYING_LAST'][0]

    atm_strike_price = strike_difference * (round(underlying_price / strike_difference))

    call_spread.loc['0'] = ['CALL', atm_strike_price, 1, np.nan]
    
    call_spread['premium'] = call_spread.apply(lambda r: get_premium(r, options_data), axis=1)
    
    deviation = round(call_spread.premium.sum()*4 / strike_difference) * strike_difference

    call_spread.loc['1'] = ['CALL', atm_strike_price + deviation, -1, np.nan]
    
    call_spread['premium'] = call_spread.apply(lambda r: get_premium(r, options_data), axis=1)

    return call_spread


# ---------------------------------- Straddle ----------------------------------

def setup_straddle(futures_price, options_data, direction='short'):
    straddle = pd.DataFrame()

    straddle['Option Type'] = ['CALL', 'PUT']
    straddle['Strike Price'] = options_data.atm
    straddle['position'] = -1

    straddle['premium'] = straddle.apply(lambda r: get_premium(r, options_data), axis=1)

    if direction == 'long':
        straddle['position'] *= -1

    straddle['premium'] = straddle.apply(lambda r: get_premium(r, options_data), axis=1)

    # net_premium = (butterfly.positions * butterfly.premium).sum()

    return straddle


# --------------------------------- Trade Analytics -------------------------------

def trade_level_analytics(round_trips):
    # Assume lot size as 5
    lot_size = 5

    # Calculate net premium 
    round_trips['trade_wise_PnL'] = round_trips['position'] * (round_trips['exit_price'] - round_trips['entry_price'])

    # Create a dataframe for storing trades
    trades = pd.DataFrame()

    # Groupby entry date
    trades_group = round_trips.groupby('entry_date')

    # Group trades from round_trips
    trades['Entry_Date'] = trades_group['entry_date'].first()
    trades['Exit_Date'] = trades_group['exit_date'].first()
    trades['Exit_Type'] = trades_group['exit_type'].first()

    # Calculate PnL for the strategy for 1 lot
    trades['PnL'] = trades_group.trade_wise_PnL.sum() * lot_size

    # Calculate turnover for trades
    trades['Turnover'] = (trades_group['exit_price'].sum() + trades_group['entry_price'].sum()) * lot_size

    # Calculate PnL after deducting trading costs and slippages
    trades['PnL_post_trading_costs_slippages'] = trades['PnL'] - trades['Turnover']*(0.01)

        # Create dataframe to store trade analytics
    analytics = pd.DataFrame(index=['Strategy'])

    # Calculate total PnL
    analytics['Total PnL'] = trades.PnL.sum()

    # Number of total trades
    analytics['total_trades'] = len(trades)

    # Profitable trades
    analytics['Number of Winners'] = len(trades.loc[trades.PnL > 0])

    # Loss-making trades
    analytics['Number of Losers'] = len(trades.loc[trades.PnL <= 0])

    # Win percentage
    analytics['Win (%)'] = 100 * analytics['Number of Winners'] / analytics.total_trades

    # Loss percentage
    analytics['Loss (%)'] = 100 * analytics['Number of Losers'] / analytics.total_trades

    # Per trade profit/loss of winning trades
    analytics['per_trade_PnL_winners'] = trades.loc[trades.PnL > 0].PnL.mean()

    # Per trade profit/loss of losing trades
    analytics['per_trade_PnL_losers'] = np.abs(trades.loc[trades.PnL <= 0].PnL.mean())

    # Calculate profit factor
    analytics['Profit Factor'] = (analytics['Win (%)'] / 100 * analytics['per_trade_PnL_winners']) / (
            analytics['Loss (%)'] / 100 * analytics['per_trade_PnL_losers'])

    return analytics.T
