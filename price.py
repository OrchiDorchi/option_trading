import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import pickle


data = pd.read_csv('spy_daily_2009_2022.csv')
vot_soft = pickle.load(open('vot_soft.pickle', "rb"))

data = data.set_index('Date')
line_graph= px.line(data['Close'],title='Daily close Price of SPY')

st.title('Bull Spread Trading AI')
st.plotly_chart(line_graph)


col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    if st.button('Run Backtest'):
        st.write('ZOMZOMZOMOZM')