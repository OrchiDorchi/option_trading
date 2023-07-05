import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import pickle
from backtest import backtest
from ml_options_util_quantra import advice
from Option import visualize_options,Call,Put
from portfolio_analytics import total_return,volatility,sharpe,annualized_return,drawdowns,sortino

st.set_page_config(page_title='Riskoptima Options', layout="centered")

done_backtest = False
analytics = None
spread = None
equity_graph = None
data = pd.read_csv('spx.csv')
vot_soft = pickle.load(open('vot_soft.pickle', "rb"))
data = data.set_index('Date')
data = data[:-1]


st.header('AI Model for Bull Call Spread Trading')

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
    ('5%', '10%', '15%','20%','30%',),horizontal=True,index=4)
# min_roi = st.radio(
#     "What is the minimum ROI (return on investment) you are willing to make?",
#     ('5%', '10%', '15%','20%','30%','50%','100%','200%'),horizontal=True,index=3)
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
    analytics_graph= px.line(analytics['Equity'],title='Equity')

    total_r = total_return(analytics['Equity'])
    total_r = '{:.2f}%'.format(100* total_r)
    annualized_r = annualized_return(analytics['Equity'])
    annualized_r = '{:.2f}%'.format(100 * annualized_r)
    drawdowns_ = drawdowns(analytics['Equity'])
    max_drawdown = '{:.2f}%'.format(drawdowns_[-1])
    volatility_ = volatility(analytics['Equity'])
    volatility_ = '{:.5f}'.format(volatility_)
    sharpe_ = sharpe(analytics['Equity'])
    sharpe_ = '{:.2f}'.format(sharpe_)
    sortino_ = sortino(analytics['Equity'])
    sortino_ = '{:.2f}'.format(sortino_)



    portfolio_analytics = pd.DataFrame(columns=['Value'])
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':total_r},name='Total Return'))
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':annualized_r},name='Annualized Return'))
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':volatility_},name='Volatility'))
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':sharpe_},name='Sharpe Ratio'))
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':sortino_},name='Sortino Ratio'))
    portfolio_analytics = portfolio_analytics.append(pd.Series({'Value':max_drawdown},name='Max. Drawdown'))

    # analytics.to_csv('analytics.csv')
    st.plotly_chart(analytics_graph)
    st.subheader('Backtesting Results')
    st.dataframe(round_trips_details)
    st.subheader('Spread Strategy Total PnLs')
    st.dataframe(trades)
    st.subheader('Trade Analytics')
    st.dataframe(trade_analytics.T)
    st.subheader('Portfolio Analytics')
    st.dataframe(portfolio_analytics)
    # drawdown_graph= px.line(y=drawdowns_,x=analytics.index,title='Maximum Drawdown')
    # drawdown_graph.update_layout(xaxis_title='Date',yaxis_title='Value')
    # st.plotly_chart(drawdown_graph)

