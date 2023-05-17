import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import pickle
from backtest import backtest
from ml_options_util_quantra import advice
from Option import visualize_options,Call,Put

st.set_page_config(page_title='Riskoptima Options', layout="centered")

done_backtest = False
analytics = None
spread = None
equity_graph = None
data = pd.read_csv('spx.csv')
vot_soft = pickle.load(open('vot_soft.pickle', "rb"))
data = data.set_index('Date')
data = data[:-1]


st.header('ML Model for Bull Call Spread Trading')

line_graph= px.line(data['Adj Close'],title='Daily close Price of SPX')
st.plotly_chart(line_graph)

col1,col2 = st.columns([2,1])
st.markdown("""
<style>
    button.step-up {display: none;}
    button.step-down {display: none;}
    div[data-baseweb] {border-radius: 4px;}
</style>""",
unsafe_allow_html=True)
st.markdown("""
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """, unsafe_allow_html=True)

with col1:
    initial_equity = st.number_input('How much money are you willing to invest?(USD)',value=5000,format='%d')

max_risk = st.radio(
    "What is the maximum percent of your investment you would accept losing?",
    ('5%', '10%', '15%','20%','30%','50%','100%'),horizontal=True,index=6)
min_roi = st.radio(
    "What is the minimum ROI (return on investment) you are willing to make?",
    ('5%', '10%', '15%','20%','30%','50%','100%','200%'),horizontal=True,index=3)
col1, col2, col3, col4, col5 = st.columns(5)

# col1, col2, col3 = st.columns(3)
# with col1:
#     take_profit = st.number_input('Take Profit %',value=40)
# with col2:
#     stop_loss = st.number_input('Stop Loss %',value=40)
# with col3:
#     confidence = st.number_input('AI Confidence %',value=50)

col1, col2, col3, col4, col5 = st.columns(5)
with col3:      
    if st.button('Run Backtest'):
        done_backtest=True
with col3:      
    if st.button('Give Advice'):
        last_close, spread = advice(initial_equity * float(max_risk.strip('%')) / 100)

if spread is not None:
    st.write('Last days close is ${:.2f}'.format(last_close))
    st.table(spread)
    call1 = Call(last_close,spread.iloc[0]['Strike Price'],30,spread.iloc[0]['premium'],'purchase')
    call2 = Call(last_close,spread.iloc[1]['Strike Price'],30,spread.iloc[1]['premium'],'write')
    st.subheader('Potential Profit Graph')
    visualize_options([call1,call2],spread.iloc[0]['Size'],3750,4000)
if done_backtest:
    analytics,round_trips_details,trades,trade_analytics = backtest(initial_equity,float(max_risk.strip('%')))

if analytics is not None:
    analytics = analytics.rename(columns={"Cumulative PnL": "Equity"})
    analytics_graph= px.line(analytics['Equity'],)
    # analytics.to_csv('analytics.csv')
    st.plotly_chart(analytics_graph)
    st.subheader('Backtesting Results')
    st.dataframe(round_trips_details)
    st.subheader('Spread Strategy Total')
    st.dataframe(trades)
    st.subheader('Trade Analytics')
    st.dataframe(trade_analytics.T)
    st.subheader('Portfolio Analytics')


