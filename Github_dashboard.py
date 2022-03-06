# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 11:47:25 2021

@author: tai
"""

import pandas as pd
import os
import requests

import streamlit as st
import datetime as dt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import numpy_financial as npf #DOWNLOAD: pip3 install numpy-financial
import plotly.express as px
import plotly.graph_objects as go

import yfinance as yf

#%% page setup
st.set_page_config(layout="wide")  # this needs to be the first Streamlit command

st.title("RENT or BUY?")
st.subheader("Set inputs on 'Control Panel' on left. Scroll down for more analysis.")
#st.markdown("*Check out the [article](https://www.crosstab.io/articles/staged-rollout-analysis) for a detailed walk-through!*")
st.sidebar.title("Control Panel")
st.sidebar.subheader("Inputs on home purchase")

col1,col2,col3 = st.columns([3,3,3])

#%% import other csv files via GitHub cloud
url_realtor = 'https://raw.githubusercontent.com/liu3388/RE_input/main/realtor.csv'
df_realtor = pd.read_csv(url_realtor)

url_zipCodes = 'https://raw.githubusercontent.com/liu3388/RE_input/main/zip_codes.csv'
df_zip = pd.read_csv(url_zipCodes)

url_rent = 'https://raw.githubusercontent.com/liu3388/RE_input/main/rent.csv'
df_rent = pd.read_csv(url_rent)

url_tax = 'https://raw.githubusercontent.com/liu3388/RE_input/main/tax.csv'
df_tax = pd.read_csv(url_tax)

url_ins = 'https://raw.githubusercontent.com/liu3388/RE_input/main/insurance.csv'
df_ins = pd.read_csv(url_ins)

url_pop = 'https://raw.githubusercontent.com/liu3388/RE_input/main/population_state_county.csv'
df_pop = pd.read_csv(url_pop)

url_USpop = 'https://raw.githubusercontent.com/liu3388/RE_input/main/population_US.csv'
df_USpop = pd.read_csv(url_USpop)

url_income = 'https://raw.githubusercontent.com/liu3388/RE_input/main/med_household_income.csv'
df_income = pd.read_csv(url_income)

#%% setup path to import csv files
# os.chdir("C:\\Tai\\RE_project\\input\\RE_input\\")
# path = os.getcwd()
# path_csv = path + "\\"

#%% import csv files via local drive
# df_zip = "zip_codes.csv"
# df_zip = pd.read_csv (path + "\\" + df_zip)
# df_rent = "rent.csv"
# df_rent = pd.read_csv (path + "\\" + df_rent)
# df_tax = "tax.csv"
# df_tax = pd.read_csv (path + "\\" + df_tax)
# df_ins = "insurance.csv"
# df_ins = pd.read_csv (path + "\\" + df_ins)
# df_pop = "population_state_county.csv"
# df_pop = pd.read_csv (path + "\\" + df_pop, encoding = "ISO-8859-1")
# df_USpop = "population_US.csv"
# df_USpop = pd.read_csv (path + "\\" + df_USpop)
# df_income = "med_household_income.csv"
# df_income = pd.read_csv (path + "\\" + df_income, encoding='ISO-8859-1')

# #import in Realtor.com data csv file and merge with file with data for zip/city/county/state/sq feet data
# df_realtor = "realtor.csv"
# df_realtor = pd.read_csv (path_csv + "\\" + df_realtor)

#%% create zip code lists and create side bar filter
#convert column 'postal_code' to str, add zeroes to zips
df_realtor['postal_code'] = df_realtor['postal_code'].astype(str)
df_realtor['postal_code'] = df_realtor['postal_code'].str.pad(5, 'left', '0')

#convert column 'zip' to str ind df_zip, add zeroes to zips
df_zip['zip'] = df_zip['zip'].astype(str)
df_zip['zip'] = df_zip['zip'].str.pad(5, 'left', '0')

#import file for: zip code, city, county, state and avg sf size data
df_realtor = df_realtor.merge(df_zip, how='left', left_on='postal_code', right_on='zip')
df_realtor = df_realtor[:-1]

#create df_chart1
df_chart1 = df_realtor

#select columns for df_chart1
df_chart1 = df_chart1[['month_date_yyyymm','postal_code', 'median_listing_price', 'state', 'county']]

df_chart1 = df_chart1.rename(columns={'month_date_yyyymm': 'date'})
df_chart1['date'] = pd.to_datetime(df_chart1['date'], format="%Y%m").dt.date

#%% create side bar filters for zip and dates
ZIP_SELECTED = st.sidebar.text_input('Type in zip code', 
                                        value = str(30096),
                                        help="Zip code of property.",
                                        key='ZIP_SELECTED')

# create start date filter on side bar
start_date = dt.date(year=2016,month=7,day=1)
DATE_SELECTED = st.sidebar.date_input('Select purchase date (data starts at: 2016-07-01)', 
                                       min_value = start_date,
                                       value = start_date,
                                       help="Begining of comparison period. Usually the purchase date of property.",
                                       key='DATE_SELECTED')

DATE_SELECTED = DATE_SELECTED.replace(day=1)


end_date = dt.date(year=2021,month=12,day=1)
END_DATE_SELECTED = st.sidebar.date_input('Select end date (latest data: 2021-12-01)', 
                                       value = end_date,
                                       help="End date of comparison period. Usually the latest month with available data.",
                                       key='END_DATE_SELECTED')

END_DATE_SELECTED = END_DATE_SELECTED.replace(day=1)


#%% User input results
df_chart1a = (df_chart1.loc[df_chart1['postal_code'] == (ZIP_SELECTED)])
df_chart1b = (df_chart1a.loc[df_chart1a['date'] == (DATE_SELECTED)])
df_chart1c = (df_chart1a.loc[df_chart1a['date'] == (END_DATE_SELECTED)])

#set up variable for current house price
current_price = df_chart1c.iloc[0]['median_listing_price']

df_chart1 = df_chart1b.append(df_chart1c)
df_chart1['date2']=df_chart1['date'].astype(str)

#%% Chart_1: home price

fig = px.bar(df_chart1, x="date2", y="median_listing_price", 
             title = 'Realtor.com median house price', 
             text="median_listing_price", barmode = 'group'
             )

with col1:
    fig.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=15,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Realtor.com median listing house price  <br>Zip code: {ZIP_SELECTED}</b>'),
        title_font_size=18,
        legend_title_font_color="black",
        yaxis_title=None,
        xaxis_title=None,
#        yaxis_range=[0, 400000],
        yaxis_tickprefix = '$',
        showlegend=False,
        title_x=0.08,
        title_y=0.925,
        width=600,
        height=430, 
        bargap=0.2
        )
    
    #add that percentage price change label
    price_change = df_chart1.iloc[1]['median_listing_price']/df_chart1.iloc[0]['median_listing_price'] -1
    my_formatter = "{:+.0%}"
    price_change = my_formatter.format(price_change)
        
    y_position = df_chart1.iloc[1]['median_listing_price']*1.10
    fig.add_annotation(text=(f'<b>{price_change}</b>'),
                  xref="x", yref="y",
                  x=0.5, y=y_position, showarrow=False, font_size=18)
        
    fig.update_traces(texttemplate='%{value:$,.0f}', textfont_size=15, textposition='inside',
                      marker_color='#0000FF')
    fig.update_xaxes(type='category', linecolor='black')
    
    #place the chart in streamlit column
    st.plotly_chart(fig)

#%% fig_2: rental trends

#convert 'zip_code' from string to integer
#zip_code_int = ZIP_SELECTED
df_rent.rename(columns={'fmr_1br': '1 bedroom', 'fmr_2br': '2 bedroom',
                          'fmr_3br': '3 bedroom', 'fmr_3br': '3 bedroom',
                          'fmr_4br': '4 bedroom'}, inplace=True)
df_rent_chart = df_rent.loc[df_rent['zip_code'] == int(ZIP_SELECTED)]
df_rent_chart = df_rent_chart[['2 bedroom', '3 bedroom', '4 bedroom', 'year']]
df_rent_chart = df_rent_chart[df_rent_chart['year'].isin(['2017', '2022'])]

# start chart coding
with col2:
    
    # Defining Custom Colors
    colors = {
        "2 bedroom": "orange",
        "3 bedroom": "#00FFFF",
        "4 bedroom": "#00FF00",
    }
    
    fig_2 = px.bar(df_rent_chart, x="year", y=["2 bedroom", "3 bedroom", "4 bedroom"], 
                     title = 'Rental trends', barmode = 'group', color_discrete_map=colors
                 )
    
    #format chart
    fig_2.update_layout(
        font_family="Arial",
        font_color="black",
        font_size=15,
        title_font_family="Arial",
        title_font_color="black",
        title = (f'<b>Rental trends: monthly rent costs <br>Zip code: {ZIP_SELECTED}</b>'),
        title_font_size=18,
        legend_title_font_color="black",
        legend_title=None,
        yaxis_title=None,
        xaxis_title=None,
    #    yaxis_range=[0, 400000],
        yaxis_tickprefix = '$', 
        showlegend=True,
        title_x=0.08,
        title_y=0.925,
        width=600,
        height=430, 
        bargap=0.175
        )
    
    #legend placement inside chart
    fig_2.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
        ))
    
    fig_2.update_traces(texttemplate='%{value:$,.0f}', textfont_size=13, 
                        textposition='inside')
    fig_2.update_xaxes(type='category', linecolor='black')
    fig_2.update_yaxes(dtick=500)
    
    #place the chart in streamlit column
    st.plotly_chart(fig_2)
    

#%% Set up session state and user input side bars for mortgage amt, mortgage terms, and interest rates
# user input side-bar for property price
if "PRICE" not in st.session_state:
    price = int(current_price)
    # set the initial default value of the slider widget
    st.session_state.PRICE = price

PROPERTY_PRICE = st.sidebar.number_input(
    'Input price of property, $',
    value = current_price,
    help="Price of property.",
    key='PRICE', 
    )

# user input side-bar for mortgage amount
if "MORTGAGE" not in st.session_state:
    # set the initial default value of the slider widget
    st.session_state.MORTGAGE = 20
    
LOAN = st.sidebar.slider(
    'Downpayment, % (usually 20%)',
    min_value = 0,
    max_value = 100,
    value = 20,
    help="Downpayment as percent of property price.",
    key='MORTGAGE', 
    )

#st.write(st.session_state.MORTGAGE) #this is just a check. Can # line when done. 

# user input side-bar for mortgage terms
if "MORTGAGE_TERMS" not in st.session_state:
    # set the initial default value of the slider widget
    st.session_state.MORTGAGE_TERMS = 30

LOAN_LIFE = st.sidebar.number_input(
    'Mortgage terms, in years (usually 15 or 30)',
    min_value=0,
    value=30,
    max_value=50,
    step=1,
    help="The life of the mortgage terms, usually 15, 20 or 30 years.",
    key='MORTGAGE_TERMS', 
    )

#st.write(st.session_state.MORTGAGE_TERMS) #this is just a check. Can # line when done. 

# user input side-bar for interest rates
if "INT_RATE" not in st.session_state:
    # set the initial default value of the slider widget
    st.session_state.INT_RATE = 3.5

INTEREST = st.sidebar.slider(
    'Input mortgage interest rate, in %',
    value=float(3.0),
    max_value=10.0,
    step=0.05,
    help="Interest rate of mortgage loan.",
    key='INT_RATE', 
    )

#st.write(st.session_state.INT_RATE) #this is just a check. Can # line when done. 

#%% set up and link variables to user input elements    
interest_rate = INTEREST / 12 / 100
n_periods = np.arange(LOAN_LIFE * 12) + 1
loan_term = LOAN_LIFE * 12
mortgage_amount = ((100-LOAN)/100) * -PROPERTY_PRICE
down_payment = LOAN/100 * PROPERTY_PRICE

#%%
with col3:
    
    def Payments(rates, n_periods, periods, mortgage_amount):

        #figure out monthly principal payment
        a = st.session_state.PrincipalPayments = npf.ppmt(rates, n_periods, periods, mortgage_amount)
        df1 = pd.DataFrame(a, columns = ['Monthly Principal'])
        
        #figure out monthly interests payment
        b = st.session_state.InterestPayments = npf.ipmt(rates, n_periods, periods, mortgage_amount)
        df2 = pd.DataFrame(b, columns = ['Monthly Interests'])
        
        #merge interest payment df and principal payment df
        df = pd.concat([df1,df2], axis=1)
        df['Monthly Payment'] = df['Monthly Principal'] + df['Monthly Interests']
            
        #figure out number of months between two dates
    #    num_months = -1*(DATE_SELECTED.year - END_DATE_SELECTED.year) * 12 + (END_DATE_SELECTED.month - DATE_SELECTED.month)
        df = df[0:12]
        
        #pull in other dfs for tax, rent, and insurance costs
        #find state
        state = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'state'].values
        county = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'county'].values
        
        Avg_property_tax = df_tax.loc[(df_tax['State'].isin(state)) & (df_tax['County'].isin(county)), 'Avg_property_tax'].values
        Avg_house_price = df_tax.loc[(df_tax['State'].isin(state)) & (df_tax['County'].isin(county)), 'Avg_house_price'].values
        county_tax_rate = Avg_property_tax / Avg_house_price
            
        state_ins_rate = df_ins.loc[(df_ins['State'].isin(state))]
        state_ins_rate = df_ins.iloc[0]['Insurance_costs_%']
        state_ins_rate = state_ins_rate[:-1]
        state_ins_rate = float(state_ins_rate)
        
        #add insurance and tax costs and costs of ownership columns
        insurance = (PROPERTY_PRICE * state_ins_rate * 0.9 / 100)/12
        df['Insurance'] = insurance
        tax = (PROPERTY_PRICE * county_tax_rate)/12
        df['Tax'] = float(tax)
        df['Ownership costs'] = df['Tax'] + df['Insurance'] + df['Monthly Interests']
        
        #pull in chadrt for historical rental trends:
        #convert 'zip_code' from string to float
        zip_code_int = float(ZIP_SELECTED)
            
        df_rent.rename(columns={'fmr_1br': '1 bedroom', 'fmr_2br': '2 bedroom',
                                  'fmr_3br': '3 bedroom', 'fmr_3br': '3 bedroom',
                                  'fmr_4br': '4 bedroom'}, inplace=True)
        df_rent_chart = df_rent.loc[df_rent['zip_code'] == zip_code_int]
        
        df_rent_chart = df_rent_chart[['2 bedroom', '3 bedroom', '4 bedroom', 'year']]
        df_rent_chart = df_rent_chart[df_rent_chart['year'].isin(['2017', '2022'])]
        
        #add rent columns to df
        br2_rent = df_rent_chart['2 bedroom'].iloc[1]
        br3_rent = df_rent_chart['3 bedroom'].iloc[1]
        br4_rent = df_rent_chart['4 bedroom'].iloc[1]    
        
        df['2 bedroom'] = br2_rent
        df['3 bedroom'] = br3_rent
        df['4 bedroom'] = br4_rent
        
        #calculate rental and costs sums
        total_int = df['Monthly Interests'].sum()
        total_ins = df['Insurance'].sum()
        total_tax = df['Tax'].sum()
        total_ownership_cost1 = total_int + total_ins + total_tax
        my_formatter = "${:,.0f}" #"{0:,.0f}"
        total_ownership_cost = my_formatter.format(total_ownership_cost1)
        total_2br = df['2 bedroom'].sum()
        total_3br = df['3 bedroom'].sum()
        total_4br = df['4 bedroom'].sum()
        data =[]
        df_chart3 = pd.DataFrame(data, columns=['Cost types', 'Ownership costs', '2 bedroom', 
                                                '3 bedroom', '4 bedroom'])
           
        df_chart3 = pd.DataFrame(columns=['Ownership costs','2 bedroom','3 bedroom',
                                          '4 bedroom'], index=['Mortgage interest', 
                                          'Tax', 'Insurance', 'Rent'])
                                                                        
        df_chart3.loc['Interest'] = pd.Series({'Ownership costs':total_int})
        df_chart3.loc['Tax'] = pd.Series({'Ownership costs':total_tax})
        df_chart3.loc['Insurance'] = pd.Series({'Ownership costs':total_ins})
        df_chart3.loc['Rent'] = pd.Series({'2 bedroom':total_2br, '3 bedroom':total_3br, 
                                            '4 bedroom':total_4br})
        
        df_chart3 = df_chart3.fillna(0)
        df_chart3 = df_chart3.T
        
        #plot chart_3
        colors = {'Interest':'darkblue',
                  'Tax':'yellow',
                  'Insurance': 'magenta',
                  'Rent': 'red'}
        
        fig_3 = px.bar(df_chart3, x = df_chart3.index,
                  y=['Interest', 'Tax', 'Insurance', 'Rent'],
                  title = 'Home ownership cost vs. renting, next 5-years',
                  barmode = 'stack', orientation=('v'),
                  color_discrete_map=colors
                  )
    
        fig_3.update_layout(
            font_family="Arial",
            font_color="black",
            font_size=15,
            title_font_family="Arial",
            title_font_color="black",
            title  = (f'<b>Est. home ownership costs vs. renting: next 12-months <br>Zip code: {ZIP_SELECTED}</b>'),
            # title='<b>Est. home ownership costs vs. renting: next 12-months</b>',
            title_font_size=18,
            legend_title_font_color="black",
            legend_font_size=15,
            legend_title=None,
            yaxis_title=None,
            xaxis_title=None,
            yaxis_tickprefix = '$',
            showlegend=True,
            title_x=0.08,
            title_y=0.925,
            width=600,
            height=430, 
            bargap=0.2,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5)
            )
        
           
        #plot sum of ownership costs as annotation text
        y_position = total_ownership_cost1*1.06
        fig_3.add_annotation(text=total_ownership_cost,
                             xref="x", yref="y",
                             x=0, y=y_position, showarrow=False)
        
        
    
        fig_3.update_traces(texttemplate='%{value:$,.0f}', textfont_size=15, textposition='inside')
        fig_3.update_xaxes(type='category', linecolor='black')
        
        #place the chart in streamlit column
        st.plotly_chart(fig_3)
        
    Payments(interest_rate, n_periods, loan_term, mortgage_amount)

#%% chart 4: SPX returns 
with col1:
    
    def chart_4():
        #calculate spx returns -- use resample!
        spx = yf.download("SPY", start=DATE_SELECTED, end=END_DATE_SELECTED)
        spx = spx.iloc[:, spx.columns.get_level_values(0)=='Adj Close']
        spx_M = spx.shift(-1).resample('M').last()
        spx_returns = spx_M['Adj Close'].iloc[-1] / spx_M['Adj Close'].iloc[0] - 1 
        
        #figure out number of months between two dates
        num_months = -1*(DATE_SELECTED.year - END_DATE_SELECTED.year) * 12 + (END_DATE_SELECTED.month - DATE_SELECTED.month)
        
        #figure out returns for SPX, buying a house full pay and buying a house with a loan
        returns_spx = "{:.0%}".format(spx_returns)
            
        #set up gauge charts
        fig_gauge1 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = spx_returns*100,
        domain = {'x': [0, 1], 'y': [0, 1]},
    #    title = {'text': "% returns", 'font': {'size': 15}},
        gauge = {
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "lightgray",
            'steps': [
                {'range': [0, 250], 'color': 'cyan'},
                {'range': [250, 400], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 490}}))
    
        fig_gauge1.update_layout(
            paper_bgcolor = "lavender", 
            font = {'color': "darkblue", 'family': "Arial", 'size': 17},
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            title='<b>Playing the stock market</b> <br> <sup>S&P 500 returns since selected purchase date, %</sup>',
            title_font_size=18,
            title_x=0.1,
            title_y=0.91,
            width=510, 
            height=380,
                )
        
        fig_gauge1.update_traces(gauge_bgcolor='white', selector=dict(type='indicator'))
        
        st.plotly_chart(fig_gauge1)
    
    #run function for chart_4
    chart_4()


#%% chart 5: unleveraged returns for house pruchse
with col2:
    
    def chart_5(rates, n_periods, periods, mortgage_amount):
        #figure out monthly principal payment
        principal = st.session_state.PrincipalPayments = npf.ppmt(rates, n_periods, periods, mortgage_amount)
        df_principal = pd.DataFrame(principal, columns = ['Monthly Principal'])
        
        #figure out number of months between two dates
        num_months = -1*(DATE_SELECTED.year - END_DATE_SELECTED.year) * 12 + (END_DATE_SELECTED.month - DATE_SELECTED.month)
        df_principal = df_principal[0:num_months]
                   
        #figure out returns for buying a house full pay and buying a house with a loan
        returns_home = df_chart1['median_listing_price'].iloc[-1] / df_chart1['median_listing_price'].iloc[0] -1
        returns_home_pct = "{:.0%}".format(returns_home)
                
        #set up gauge charts
        fig_gauge2 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = returns_home*100,
        domain = {'x': [0, 1], 'y': [0, 1]},
    #    title = {'text': "% returns", 'font': {'size': 15}},
        gauge = {
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "lightgray",
            'steps': [
                {'range': [0, 250], 'color': 'cyan'},
                {'range': [250, 400], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 490}}))
    
        fig_gauge2.update_layout(
            paper_bgcolor = "lavender", 
            font = {'color': "darkblue", 'family': "Arial", 'size': 17},
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            title='<b>Returns on home purchase, full pay</b> <br> <sup>House price returns selected purchase date, %</sup>',
            title_font_size=18,
            title_x=0.1,
            title_y=0.91,
            width=510, 
            height=380,
                )
        
        fig_gauge2.update_traces(gauge_bgcolor='white', selector=dict(type='indicator'))
        
        st.plotly_chart(fig_gauge2)
        
    #run function for chart_5            
    chart_5(interest_rate, n_periods, loan_term, mortgage_amount)


#%% chart 6: unleveraged returns for house pruchse
with col3:
    
    def chart_6(rates, n_periods, periods, mortgage_amount):
        #figure out monthly principal payment
        principal = st.session_state.PrincipalPayments = npf.ppmt(rates, n_periods, periods, mortgage_amount)
        df_principal = pd.DataFrame(principal, columns = ['Monthly Principal'])
        
        #figure out number of months between two dates
        num_months = -1*(DATE_SELECTED.year - END_DATE_SELECTED.year) * 12 + (END_DATE_SELECTED.month - DATE_SELECTED.month)
        df_principal = df_principal[0:num_months]
        total_principal = df_principal['Monthly Principal'].sum()
                   
        #figure out returns for buying a house full pay and buying a house with a loan
        price_chg = df_chart1['median_listing_price'].iloc[-1] - df_chart1['median_listing_price'].iloc[0]
                
        returns_home_lev = ((down_payment + total_principal + price_chg) / down_payment)-1
        returns_home_lev_pct = "{:.0%}".format(returns_home_lev)
        
        #set up gauge charts
        fig_gauge3 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = returns_home_lev*100,
        domain = {'x': [0, 1], 'y': [0, 1]},
#        title = {'text': "% returns", 'font': {'size': 15}},
        gauge = {
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "lightgray",
            'steps': [
                {'range': [0, 250], 'color': 'cyan'},
                {'range': [250, 400], 'color': 'royalblue'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 490}}))
    
        fig_gauge3.update_layout(
            paper_bgcolor = "lavender", 
            font = {'color': "darkblue", 'family': "Arial", 'size': 17},
            font_family="Arial",
            font_color="black",
            title_font_family="Arial",
            title_font_color="black",
            title='<b>Buying the house with a mortgage</b> <br> <sup>Leveraged house price returns since selected purchase date, %</sup>',
            title_font_size=18,
            title_x=0.1,
            title_y=0.91,
            width=510,
            height=380,
                )
        
        fig_gauge3.update_traces(gauge_bgcolor='white', selector=dict(type='indicator'))
        
        st.plotly_chart(fig_gauge3)
        
    #run function for chart_5            
    chart_6(interest_rate, n_periods, loan_term, mortgage_amount)


#%% set up for population charts
state = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'state'].values
county = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'county'].values

Year_1 = str(2016)
Year_2 = str(2017)
Year_3 = str(2018)
Year_4 = str(2019)
Year_5 = str(2020)
        
df_pop = df_pop.rename(columns={'STNAME': 'State', 'CTYNAME': 'County'})
county_pop = df_pop.loc[(df_pop['State'].isin(state))]
county_pop = df_pop.loc[(df_pop['State'].isin(state)) & (df_pop['County'].isin(county))]
county_pop = county_pop[[Year_1, Year_2, Year_3, Year_4, Year_5]]
        
state_pop = df_pop.loc[(df_pop['State'].isin(state)) & (df_pop['County'].isin(state))]
state_pop = state_pop[[Year_1, Year_2, Year_3, Year_4, Year_5]]
        
US_pop = df_USpop
US_pop['year'] = US_pop['DATE'].str[-4:]
US_pop = US_pop.loc[(US_pop['year'] == Year_1) | (US_pop['year'] == Year_5)]
del US_pop['DATE']
    
US_pop.iloc[0] = pd.to_numeric(US_pop.iloc[0].str.replace(',', ''))
US_pop.iloc[1] = pd.to_numeric(US_pop.iloc[1].str.replace(',', ''))

pop_rate_county = county_pop[Year_5].iloc[0] / county_pop[Year_1].iloc[0] - 1
pop_rate_state = state_pop[Year_5].iloc[0] / state_pop[Year_1].iloc[0] - 1
pop_rate_US = US_pop.iloc[1][0] / US_pop.iloc[0][0] - 1

state1 = str(state).strip("[]'") 
county1 = str(county).strip("[]'")


#%% first population chart starts here
with col1: 
    def chart_4():
        df_chart4 = pd.DataFrame(columns=['United States', state1, county1], index=['Population growth rate'])
    
        df_chart4.loc['Population growth rate'] = pd.Series({'United States': pop_rate_US, 
                                          state1: pop_rate_state, 
                                          county1: pop_rate_county})
    
        df_chart4 = df_chart4.T
        df_chart4['Region'] = df_chart4.index
        
        colors = {
            "United States": "orange",
            state1: "#00FFFF",
            county1: "#00FF00",
            }
        
        fig_4 = px.bar(df_chart4, y='Region', x='Population growth rate', 
                 title = 'Regional population growth rates', 
                 text= 'Population growth rate', barmode = 'group', orientation=('h'),
                 )
        
        colors = {'U.S.':'darkblue',
                      state1:'yellow',
                      county1: 'magenta',
                      }
        
        fig_4.update_layout(
            font_family="Arial",
            font_color="black",
            font_size=15,
            title_font_family="Arial",
            title_font_color="black",
            title='<b>County/state/U.S. population growth rates, 2016-2020</b>',
            title_font_size=18,
            legend_title_font_color="black",
            legend_title=None,
            yaxis_title=None,
            xaxis_title=None,
        #    yaxis_range=[0, 400000],
            yaxis_tickprefix = '', 
            yaxis_ticksuffix = '',
            showlegend=False,
            title_x=0.03,
            title_y=0.925,
            width=600,
            height=430, 
            bargap=0.175
            )
        
        fig_4.layout.xaxis.tickformat = ',.0%'
        
        fig_4.update_traces(texttemplate='%{value:0,.2%}', textfont_size=15, 
                            textposition='inside', marker_color='#9A32CD')
        fig_4.update_xaxes(linecolor='black')
        
        #place chart in proper column
        st.plotly_chart(fig_4)
        
    #run function for chart_5            
    chart_4()
    
#%% testing out a link

# with col2:
#     st.markdown("*Check out the [article](https://www.crosstab.io/articles/staged-rollout-analysis) for a detailed walk-through!*")
    
   
#%% setup income tables (absolute $ amt)
income_county = df_income.loc[(df_income['State_Alpha'] == state1) & 
                              (df_income['County_Name'] == county1)].T

#delete all duplicate rows
income_county = income_county.drop_duplicates()


income_US = df_income.loc[(df_income['State_Alpha'] == 'US') & 
                              (df_income['County_Name']== 'United States')].T

df_chart5 = pd.merge(income_US, income_county, left_index=True, right_index=True).reset_index()

#reformat df for first chart on income
df_inc_chart = df_chart5.iloc[3:]
df_inc_chart = df_inc_chart.rename(columns=df_inc_chart.iloc[0]).iloc[1:]
df_inc_chart.rename({'County_Name': 'Year'}, axis=1, inplace=True)
df_inc_chart['United States'] = df_inc_chart['United States'].astype(float)
df_inc_chart[county1] = df_inc_chart[county1].astype(float)
df_inc_chart['Year'] = df_inc_chart['Year'].astype(str)
df_inc_chart['Year'].astype(int)
df_inc_chart = df_inc_chart.sort_values(by='Year', ascending=True)

#%% first income per capita chart (absolute $ amt)
with col2:
    def chart_income():
        # Defining Custom Colors
        colors = {
            "United States": "#00FF7F",
            county1: "#63B8FF",
            }
        
        fig_5 = px.bar(df_inc_chart, 
                       x='Year', y=['United States', county1], 
                       title = 'Median household income', barmode = 'group', 
                       color_discrete_map=colors                      
                       )
    
        #format chart
        fig_5.update_layout(
            font_family="Arial",
            font_color="black",
            font_size=15,
            title_font_family="Arial",
            title_font_color="black",
            title='<b>Median household income</b>',
            title_font_size=18,
            legend_title_font_color="black",
            legend_title=None,
            yaxis_title=None,
            xaxis_title=None,
            # yaxis_range=[, ],
            yaxis_tickprefix = '$', 
            showlegend=True,
            title_x=0.08,
            title_y=0.925,
            width=600,
            height=430, 
            bargap=0.175
            )
        
        #legend placement inside chart
        fig_5.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.9
            ))
        
        fig_5.update_traces(texttemplate='%{value:$,.0f}', textfont_size=13, 
                            textposition='inside')
        fig_5.update_xaxes(type='category', linecolor='black')
        # fig_5.update_yaxes(dtick=500)
        
        # #place the chart in streamlit column
        st.plotly_chart(fig_5)
        
    #run function for chart_5            
    chart_income()
        
#%% income chart two: percentage comparisons
#reformat df for first chart on income
df_inc_chart2 = df_inc_chart.copy()
df_inc_chart2.set_index('Year', inplace=True)
df_inc_chart2.loc['2021 %'] = df_inc_chart2.loc['2021'] / df_inc_chart2.loc['2020'] -1
df_inc_chart2.loc['2020 %'] = df_inc_chart2.loc['2020'] / df_inc_chart2.loc['2019'] -1
df_inc_chart2.loc['2019 %'] = df_inc_chart2.loc['2019'] / df_inc_chart2.loc['2018'] -1
df_inc_chart2 = df_inc_chart2.tail(3)
df_inc_chart2 = df_inc_chart2.reset_index()
df_inc_chart2['Year'] = df_inc_chart2['Year'].replace({'%':''}, regex=True)
df_inc_chart2['Year'].astype(int)
df_inc_chart2 = df_inc_chart2.sort_values(by='Year', ascending=True)


#%% income chart 2: 

with col3:
    def chart_income():
        # Defining Custom Colors
        colors = {
            "United States": "lightgreen",
            county1: "cyan",
        }
        
        fig_6 = px.bar(df_inc_chart2, 
                       x='Year', y=['United States', county1], 
                       title = 'Median household income, year-on-year change', barmode = 'group', 
                       color_discrete_map=colors                      
                       )
    
        #format chart
        fig_6.update_layout(
            font_family="Arial",
            font_color="black",
            font_size=15,
            title_font_family="Arial",
            title_font_color="black",
            title='<b>Median household income, year-on-year change</b>',
            title_font_size=18,
            legend_title_font_color="black",
            legend_title=None,
            yaxis_title=None,
            xaxis_title=None,
            # yaxis_range=[0, ],
            # yaxis_ticksuffix = '%', 
            showlegend=True,
            title_x=0.08,
            title_y=0.925,
            width=600,
            height=430, 
            bargap=0.175
            )
        
        #legend placement inside chart
        fig_6.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
            ))
        
        fig_6.layout.yaxis.tickformat = ',.0%'
        
        fig_6.update_traces(texttemplate='%{value:0,.1%}', textfont_size=13, 
                            textposition='inside')
        fig_6.update_xaxes(type='category', linecolor='black')
        # fig_5.update_yaxes(dtick=500)
        
        #place the chart in streamlit column
        st.plotly_chart(fig_6)
        
    #run function for chart_5            
    chart_income()

#%%
with col1:
    
    def Payments(rates, n_periods, periods, mortgage_amount):

        #figure out monthly principal payment
        a = st.session_state.PrincipalPayments = npf.ppmt(rates, n_periods, periods, mortgage_amount)
        df1 = pd.DataFrame(a, columns = ['Monthly Principal'])
        
        #figure out monthly interests payment
        b = st.session_state.InterestPayments = npf.ipmt(rates, n_periods, periods, mortgage_amount)
        df2 = pd.DataFrame(b, columns = ['Monthly Interests'])
        
        #merge interest payment df and principal payment df
        df = pd.concat([df1,df2], axis=1)
        df['Monthly Payment'] = df['Monthly Principal'] + df['Monthly Interests']
            
        #figure out number of months between two dates
    #    num_months = -1*(DATE_SELECTED.year - END_DATE_SELECTED.year) * 12 + (END_DATE_SELECTED.month - DATE_SELECTED.month)
        df = df[0:12]
        
        #pull in other dfs for tax, rent, and insurance costs
        #find state
        state = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'state'].values
        county = df_chart1.loc[(df_chart1['postal_code'] == (ZIP_SELECTED)) & (df_chart1['date']==(DATE_SELECTED)), 'county'].values
        
        Avg_property_tax = df_tax.loc[(df_tax['State'].isin(state)) & (df_tax['County'].isin(county)), 'Avg_property_tax'].values
        Avg_house_price = df_tax.loc[(df_tax['State'].isin(state)) & (df_tax['County'].isin(county)), 'Avg_house_price'].values
        county_tax_rate = Avg_property_tax / Avg_house_price
            
        state_ins_rate = df_ins.loc[(df_ins['State'].isin(state))]
        state_ins_rate = df_ins.iloc[0]['Insurance_costs_%']
        state_ins_rate = state_ins_rate[:-1]
        state_ins_rate = float(state_ins_rate)
        
        #add insurance and tax costs and costs of ownership columns
        insurance = (PROPERTY_PRICE * state_ins_rate * 0.9 / 100)/12
        df['Insurance'] = insurance
        tax = (PROPERTY_PRICE * county_tax_rate)/12
        df['Tax'] = float(tax)
        df['Ownership cashflow'] = df['Monthly Principal'] + df['Tax'] + df['Insurance'] + df['Monthly Interests']
        
        #pull in chadrt for historical rental trends:
        #convert 'zip_code' from string to float
        zip_code_int = float(ZIP_SELECTED)
            
        df_rent.rename(columns={'fmr_1br': '1 bedroom', 'fmr_2br': '2 bedroom',
                                  'fmr_3br': '3 bedroom', 'fmr_3br': '3 bedroom',
                                  'fmr_4br': '4 bedroom'}, inplace=True)
        df_rent_chart = df_rent.loc[df_rent['zip_code'] == zip_code_int]
        
        df_rent_chart = df_rent_chart[['2 bedroom', '3 bedroom', '4 bedroom', 'year']]
        df_rent_chart = df_rent_chart[df_rent_chart['year'].isin(['2017', '2022'])]
        
        #add rent columns to df
        br2_rent = df_rent_chart['2 bedroom'].iloc[1]
        br3_rent = df_rent_chart['3 bedroom'].iloc[1]
        br4_rent = df_rent_chart['4 bedroom'].iloc[1]    
        
        df['2 bedroom'] = br2_rent
        df['3 bedroom'] = br3_rent
        df['4 bedroom'] = br4_rent
        
        #calculate rental and costs sums
        total_int = df['Monthly Interests'].sum()
        total_ppl = df['Monthly Principal'].sum()
        total_ins = df['Insurance'].sum()
        total_tax = df['Tax'].sum()
        total_ownership_cost1 = total_int + total_ppl + total_ins + total_tax
        my_formatter = "${:,.0f}" #"{0:,.0f}"
        total_ownership_cost = my_formatter.format(total_ownership_cost1)
        total_2br = df['2 bedroom'].sum()
        total_3br = df['3 bedroom'].sum()
        total_4br = df['4 bedroom'].sum()
        data =[]
        df_chart3 = pd.DataFrame(data, columns=['cashflow types', 'Ownership cashflow', '2 bedroom', 
                                                '3 bedroom', '4 bedroom'])
           
        df_chart3 = pd.DataFrame(columns=['Ownership <br> cashflow','2 bedroom','3 bedroom',
                                          '4 bedroom'], index=['Mortgage interest', 'Principal repayment'
                                          'Tax', 'Insurance', 'Rent'])
                                                                        
        df_chart3.loc['Interest'] = pd.Series({'Ownership <br> cashflow':total_int})
        df_chart3.loc['Principal'] = pd.Series({'Ownership <br> cashflow':total_ppl})
        df_chart3.loc['Tax'] = pd.Series({'Ownership <br> cashflow':total_tax})
        df_chart3.loc['Insurance'] = pd.Series({'Ownership <br> cashflow':total_ins})
        df_chart3.loc['Rent'] = pd.Series({'2 bedroom':total_2br, '3 bedroom':total_3br, 
                                            '4 bedroom':total_4br})
        
        df_chart3 = df_chart3.fillna(0)
        df_chart3 = df_chart3.T
        
        #plot chart_3
        colors = {'Interest':'darkblue',
                  'Principal': 'green',
                  'Tax':'yellow',
                  'Insurance': 'magenta',
                  'Rent': 'red'}
        
        fig_3 = px.bar(df_chart3, x = df_chart3.index,
                  y=['Interest', 'Principal', 'Tax', 'Insurance', 'Rent'],
                  title = 'Home ownership cashflow vs. renting, next 5-years',
                  barmode = 'stack', orientation=('v'),
                  color_discrete_map=colors
                  )
    
        fig_3.update_layout(
            font_family="Arial",
            font_color="black",
            font_size=15,
            title_font_family="Arial",
            title_font_color="black",
            title = (f'<b>Est. home ownership cashflow vs. renting: next 12-months <br>Zip code: {ZIP_SELECTED}</b>'),
            title_font_size=18,
            legend_title_font_color="black",
            legend_font_size=15,
            legend_title=None,
            yaxis_title=None,
            xaxis_title=None,
            yaxis_tickprefix = '$',
            showlegend=True,
            title_x=0.08,
            title_y=0.93,
            width=620,
            height=430, 
            bargap=0.2,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5)
            )
        
        #plot sum of ownership costs as annotation text
        y_position = total_ownership_cost1*1.06
        fig_3.add_annotation(text=total_ownership_cost,
                  xref="x", yref="y",
                  x=0, y=y_position, showarrow=False)

        #update charts
        fig_3.update_traces(texttemplate='%{value:$,.0f}', textfont_size=15, textposition='inside')
        fig_3.update_xaxes(type='category', linecolor='black')
        
        #place the chart in streamlit column
        st.plotly_chart(fig_3)
        
    Payments(interest_rate, n_periods, loan_term, mortgage_amount)

#%% 
#streamlit run C:\Tai\RE_project\Github\script\Github_dashboard.py

