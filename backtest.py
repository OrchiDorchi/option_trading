# For data manipulation
import numpy as np
import pandas as pd
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Helper functions
import sys
sys.path.append('..')
from ml_options_util_quantra import get_premium, setup_call_spread

def add_to_mtm(mark_to_market, option_strategy, trading_date):
    option_strategy['Date'] = trading_date
    mark_to_market = pd.concat([mark_to_market, option_strategy])
    return mark_to_market

def backtest():
    options_data = pd.read_pickle(
    'spx_eom_expiry_options_2010_2022.bz2')
    options_data.columns = options_data.columns.str.replace(
        "[", "").str.replace("]", "").str.strip()
    data = pd.read_csv('spy_signals_2018_2022.csv', index_col=0)
    data['signal'] = data['predicted_signal']
    config = {
    'stop_loss_percentage': 40,
    'take_profit_percentage': 40,
    'days_to_exit_before_expiry': 1
    }
    round_trips_details = pd.DataFrame()
    trades = pd.DataFrame()
    mark_to_market = pd.DataFrame()
    current_position = 0
    trade_num = 0
    cum_pnl = 0

    exit_flag = False

    start_date = data.index[0]
    day_index = 0
    max_day = data.shape[0]
    ph =st.empty()
    completion_bar = st.progress(0,'Running Backtest...')
    for i in data.loc[start_date:].index:
        completion_bar.progress(day_index/max_day,'Backtest running...')
        day_index+=1
        if (current_position == 0) & (data.loc[i, 'signal'] != 0):
            try:
                options_data_daily = options_data.loc[i]
            except:
                continue

            if data.loc[i, 'signal'] == 1:
                spread = setup_call_spread(options_data_daily, 10)

            else:
                continue

            if (spread.premium.isna().sum() > 0) or ((spread.premium == 0).sum() > 0):
                # print(
                #     f"\x1b[31mStrike price not liquid so we will ignore this trading opportunity {i}\x1b[0m")
                continue

            trades = spread.copy()
            trades['entry_date'] = i
            trades.rename(columns={'premium': 'entry_price'}, inplace=True)

            net_premium = round((spread.position * spread.premium).sum(), 1)

            premium_sign = np.sign(net_premium)
            sl = net_premium * \
                (1 - config['stop_loss_percentage']*premium_sign/100)
            tp = net_premium * \
                (1 + config['take_profit_percentage']*premium_sign/100)

            current_position = data.loc[i, 'signal']

            mark_to_market = add_to_mtm(mark_to_market, spread, i)

            trade_num += 1
            # print("-"*30)

            # print(
            #     f"Trade No: {trade_num} | Entry | Date: {i} | Premium: {net_premium*-1} | Position: {current_position}")

        elif current_position != 0:
            try:
                options_data_daily = options_data.loc[i]
            except:
                continue

            spread['premium'] = spread.apply(
                lambda r: get_premium(r, options_data_daily), axis=1)
            net_premium = (spread.position * spread.premium).sum()

            mark_to_market = add_to_mtm(mark_to_market, spread, i)

            if data.loc[i, 'signal'] != current_position:
                exit_type = 'Expiry or Signal Based'
                exit_flag = True

            elif net_premium < sl:
                exit_type = 'SL'
                exit_flag = True

            elif net_premium > tp:
                exit_type = 'TP'
                exit_flag = True

            if exit_flag:
                if spread.premium.isna().sum() > 0:
                    # print(
                    #     f"Data missing for the required strike prices on {i}, Not adding to trade logs.")
                    current_position = 0
                    continue
                trades['exit_date'] = i
                trades['exit_type'] = exit_type
                trades['exit_price'] = spread.premium

            
                round_trips_details = pd.concat([round_trips_details, trades])
                net_premium = round((spread.position * spread.premium).sum(), 1)
                entry_net_premium = (trades.position * trades.entry_price).sum()
                trade_pnl = round(net_premium - entry_net_premium, 1)

                cum_pnl += trade_pnl
                cum_pnl = round(cum_pnl, 1)

                # print(
                #     f"Trade No: {trade_num} | Exit Type: {exit_type} | Date: {i} | Premium: {net_premium} | PnL: {trade_pnl} | Cum PnL: {cum_pnl}")

                current_position = 0
                exit_flag = False
    mark_to_market['net_premium'] = mark_to_market.position * \
    mark_to_market.premium

    # Strategy analytics
    analytics = pd.DataFrame()
    analytics['change_in_pnl'] = mark_to_market.groupby(
        'Date').net_premium.sum().diff()
    analytics.loc[analytics.index.isin(
        round_trips_details.entry_date), 'change_in_pnl'] = 0

    # Calculate cumulative PnL
    analytics['Cumulative PnL'] = analytics['change_in_pnl'].cumsum()

    completion_bar.empty()

    round_trips_details['pnl'] = round_trips_details['position'] * \
    (round_trips_details['exit_price']-round_trips_details['entry_price'])


    lot_size=100
    trades = pd.DataFrame()
    trades_group = round_trips_details.groupby('entry_date')
    trades['Entry_Date'] = trades_group['entry_date'].first()
    trades['Exit_Date'] = trades_group['exit_date'].first()
    trades['Exit_Type'] = trades_group['exit_type'].first()
    trades['PnL'] = trades_group.pnl.sum() * lot_size

    trades['Turnover'] = (trades_group['exit_price'].sum() +
                        trades_group['entry_price'].sum()) * lot_size
    trades.reset_index(inplace=True)
    trades.drop(['entry_date'],axis=1,inplace=True)

    trade_analytics = pd.DataFrame(index=['ML_Model'])

    trade_analytics['Total_PnL'] = trades['PnL'].sum()
    trade_analytics['Total_Trades'] = len(trades)
    trade_analytics['Winners'] = len(trades.loc[trades.PnL >= 0])
    trade_analytics['Losers'] = len(trades.loc[trades.PnL < 0])
    trade_analytics['Win_Percentage'] = 100 * \
        (trade_analytics['Winners']/trade_analytics['Total_Trades'])
    trade_analytics['Loss_Percentage'] = 100 * \
        (trade_analytics['Losers']/trade_analytics['Total_Trades'])
    trade_analytics['per_trade_profit_winners'] = trades.loc[trades.PnL >
                                                    0].PnL.mean()
    trade_analytics['per_trade_loss_losers'] = abs(
        trades.loc[trades.PnL < 0].PnL.mean())
    trade_analytics['Profit Factor'] = (trade_analytics['Win_Percentage']*trade_analytics['per_trade_profit_winners']) / \
    (trade_analytics['Loss_Percentage']*trade_analytics['per_trade_loss_losers'])
    round_trips_details['position'] = np.where(round_trips_details['position'] > 0, 'LONG', 'SHORT')
    round_trips_details = round_trips_details.set_index('position')
    return analytics,round_trips_details,trades,trade_analytics