import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
class Option:
    spot_price = 0
    strike_price = 0
    time_to_maturity = 0
    premium = 0
    position = 'purchase'

    def __init__(self, spot_price, strike_price, time_to_maturity, premium, position):
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.time_to_maturity = time_to_maturity
        self.premium = premium
        self.position = position


class Call(Option):
    def __init__(self, spot_price, strike_price, time_to_maturity, premium, position):
        if position not in ['purchase', 'write']:
            raise Exception("Position should be either 'purchase' or 'write'.")
        Option.__init__(self, spot_price, strike_price,
                        time_to_maturity, premium, position)


class Put(Option):
    def __init__(self, spot_price, strike_price, time_to_maturity, premium, position):
        if position not in ['purchase', 'write']:
            raise Exception("Position should be either 'purchase' or 'write'.")
        Option.__init__(self, spot_price, strike_price,
                        time_to_maturity, premium, position)


def payoff_call_purchase(S, K, P, start, end):
    price_payoff = {}
    for price in range(start, end+1):
        price_payoff[price] = max(price-K-P, -P)
    return price_payoff


def payoff_put_purchase(S, K, P, start, end):
    price_payoff = {}
    for price in range(start, end+1):
        price_payoff[price] = max(K-price-P, -P)
    return price_payoff


def payoff_call_write(S, K, P, start, end):
    price_payoff = {}
    for price in range(start, end+1):
        price_payoff[price] = -max(price-K-P, -P)
    return price_payoff


def payoff_put_write(S, K, P, start, end):
    price_payoff = {}
    for price in range(start, end+1):
        price_payoff[price] = -max(K-price-P, -P)
    return price_payoff


def visualize_options(options, size,start, end):
    payoffs = []
    price_range = []
    for option in options:
        payoff = {}
        if isinstance(option, Call):
            if option.position == 'purchase':
                payoff = payoff_call_purchase(
                    option.spot_price, option.strike_price, option.premium, start, end)
            else:
                payoff = payoff_call_write(
                    option.spot_price, option.strike_price, option.premium, start, end)
            if len(price_range)<=0:
                price_range = list(payoff.keys())
        elif isinstance(option, Put):
            if option.position == 'purchase':
                payoff = payoff_put_purchase(
                    option.spot_price, option.strike_price, option.premium, start, end)
            else:
                payoff = payoff_put_write(
                    option.spot_price, option.strike_price, option.premium, start, end)
            if len(price_range)<=0:
                price_range = list(payoff.keys())
        payoffs.append(np.array(list(payoff.values()))*size)
    sum = np.sum(payoffs,axis=0)
    df = pd.DataFrame({f'LONG CALL {options[0].strike_price}':payoffs[0],f'SHORT CALL {options[1].strike_price}':payoffs[1],'TOTAL':sum})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=price_range,
        y=payoffs[0],
        line = {'dash':'dot','color':'rgba(20,108,196,0.5)'},
        name = f'LONG CALL {options[0].strike_price}',
    ))
    fig.add_trace(go.Scatter(
        x=price_range,
        y=payoffs[1],
        line = {'dash':'dot','color':'rgba(20,108,196,0.5)'},
        name = f'SHORT CALL {options[1].strike_price}',
    ))
    fig.add_trace(go.Scatter(
        x=price_range,
        y=sum,
        name = 'TOTAL',
        line={'color':'rgba(20,108,196,1)'}
    ))
    fig.add_hline(0,line_color='rgba(0, 0, 0, 0.5)')
    line_graph= px.line(df,x=price_range,y=df.columns)
    fig.update_layout(xaxis_title='Spot Price',yaxis_title='Profit $')
    st.plotly_chart(fig) 


