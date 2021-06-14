#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 22:30:52 2021
First step towards a charting tool for ATF
@author: cakfinance
"""
import streamlit as st
import pandas as pd
import DataHandler as dh
import configure
import altair as at
from datetime import datetime
import base64
import io

@st.cache
#This is to make sure that API is onyl called when necessary
def get_names(name_list): 
    return STOCK.search(stock_list)

@st.cache
#This is to make sure that API is onyl called when necessary
def get_prices(ticker_list, startdate, enddate):
    return STOCK.get_eod_data(ticker_list, startdate, enddate)

@st.cache
#This is to get information
def get_info(ticker_list):
    return STOCK.search(ticker_list)

@st.cache
#This is to get fundamental data
def get_fundamental(ticker_list):
    return STOCK.eq_fundamentals(ticker_list, filters='General::Description')
#===============

st.title('Stock Search and Charting Tool')

# Define variable
STOCK = dh.Equity()
universe_list = []
galaxy_list = []
stock_list =[]
selection_list = []
selection_list_univ = []
ticker_list = []
price_frame = pd.DataFrame(columns=['symbol', 'date', 'price'])

#==================
# Read universe list
UNIVERSES = configure.STATIC_DATA().UNIVERSES
universe_list = list(UNIVERSES.keys())

# Select an universe
universe = st.multiselect('Select Universe', universe_list)
if len(universe) > 0:
    for galaxy in universe:
        galaxy_list.append(UNIVERSES[galaxy])
    
    stock_univ = STOCK.eq_fundamentals(galaxy_list, filters='')
    for galaxy in galaxy_list:
       for key in stock_univ[galaxy]['Components'].keys():
           root = stock_univ[galaxy]['Components'][key]
           selection_list_univ.append(root['Name']+': '+root['Code']+'.'+root['Exchange'])
#==================

# Read list of stocks
stocks = st.text_area('Input Name(s) or ticker(s)', height=100).split(',')

# Create list of stocks
for stock in stocks:
    stock_list.append(stock)
 
# Only query data provider if stock_list has content
if stock_list[0] != "":
    result = get_names(stock_list)
    
    for stock in stock_list:
        root = result[stock]
        for item in root:
            if item['ISIN']:
                selection_list.append(item['Name']+': '+item['Code']+'.'+item['Exchange'] )

#==================
# Create entry for dropdown

selection_list = selection_list+selection_list_univ
                
selected = st.multiselect('Please Select the Security from the Dropdown', selection_list)
    
for item in selected:
     ticker = item.split(':')[1]
     ticker_list.append(ticker.strip())

#==================
#Download prices  
start_date = st.date_input("Start Date", datetime(2015, 1, 1))
end_date = st.date_input('End Date')
prices = get_prices(ticker_list, start_date, end_date)

#==================
#create empty dataframe with dates as index
if len(ticker_list) > 0:
    NORM = st.radio('', ('Compare', 'Normalise'))
    for ticker in ticker_list :
        temp_df = pd.DataFrame(columns=['symbol', 'date', 'price'])
        temp_df['symbol'] = [ticker] * prices[ticker].shape[0]
        temp_df['date'] = list(prices[ticker].index)
        temp_df['date'] = pd.to_datetime(temp_df['date'], format='%Y-%m-%d')
        if NORM == 'Normalise':
            temp_df['price'] = list(prices[ticker]['Adjusted_close'] * 100/prices[ticker]['Adjusted_close'].iloc[0])
        else:
            temp_df['price'] = list(prices[ticker]['Adjusted_close'])
        price_frame = price_frame.append(temp_df)
    

    #show multiple securities in one chart
    chart = at.Chart(price_frame).mark_line().encode(at.X('date:T'),at.Y('price:Q'),color='symbol')
    st.write(chart.configure_view(continuousHeight=400,continuousWidth=750))
    
    if st.button('Create Excel'):
        excel_df = pd.DataFrame(index=prices[ticker_list[0]].index)
        for ticker in ticker_list:
            if NORM == 'Normalise':
                excel_df[ticker] = list(prices[ticker]['Adjusted_close']* 100/prices[ticker]['Adjusted_close'].iloc[0])
            else:
                excel_df[ticker] = list(prices[ticker]['Adjusted_close'])
        time_stamp = datetime.now().strftime("%m%d%Y %H%M%S")
        towrite = io.BytesIO()
        downloaded_file = excel_df.to_excel(towrite, encoding='utf-8', index=False, header=True)
        towrite.seek(0)
        b64 = base64.b64encode(towrite.read()).decode()
        file_name = ('securities'+time_stamp+'.xlsx')
        linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="'+file_name+'.xlsx">Download excel file</a>'
        st.markdown(linko, unsafe_allow_html=True)

    short_info = get_info(ticker_list)
    long_info = get_fundamental(ticker_list)
    
    # Show  information on companies
    for ticker in ticker_list:
        short_root = short_info[ticker][0]
        short = '**' + short_root['Name'] + ' (' + short_root['Code'] + ':' + short_root['Exchange'] + ') ' + short_root['Currency'] + ' ' + str(short_root['previousClose']) + '**'
        long = long_info[ticker]
        st.write(20*'_')
        st.markdown(short)
        st.write(20*'_')
        st.write(long)
        st.write(20*'_')
