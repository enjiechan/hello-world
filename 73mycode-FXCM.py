# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 21:14:01 2020

@author: User
"""


import fxcmpy
import numpy as np
from stocktrends import Renko
import statsmodels.api as sm
import time
import copy 

token_path="C:\\Users\\User\\Documents\\NUS\\Extra Modules\\Algorithmic Trading & Quantitative Analysis using Python\\Section 8-Building Automated Trading System on a Shoestring Budget\\FXCMkey.txt"
con=fxcmpy.fxcmpy(access_token=open(token_path,'r').read(),log_level='error',server='demo')

pairs=['EUR/USD','GBP/USD','USD/CHF','AUD/USD','USD/CAD']
pos_size=10

def MACD(DF,a,b,c):
    df=DF.copy()
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df['MACD'],df['Signal'])

def ATR(DF,n):
    df=DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR']=df['TR'].rolling(n).mean()
    df=df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df

def slope(ser,n):
    slopes=[i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y=ser[i-n:i]
        x=np.array(range(n))
        y_scaled=(y-y.min())/(y.max()-y.min())
        x_scaled=(x-x.min())/(x.max()-x.min())
        x_scaled=sm.add_constant(x_scaled)
        model=sm.OLS(y_scaled,x_scaled)
        results=model.fit()
        slopes.append(results.params[-1])
        slope_angle=np.rad2deg(np.arctan(np.array(slopes)))
    return np.array(slope_angle)

def renko_DF(DF):
    df=DF.copy()
    df.reset_index(inplace=True)
    df=df.iloc[:,[0,1,2,3,4,5]]  #different from 40mycode
    df.columns=['date','open','high','low','close','volume']
    df2=Renko(df)
    df2.brick_size=round(ATR(DF,120)['ATR'][-1],4) #different from 40mycode
    renko_df=df2.get_ohlc_data()
    renko_df['bar_num']=np.where(renko_df['uptrend']==True,1,np.where(renko_df['uptrend']==False,-1,0))
    for i in range(1,len(renko_df['bar_num'])):
        if renko_df['bar_num'][i]>0 and renko_df['bar_num'][i-1]>0:
            renko_df['bar_num'][i]+=renko_df['bar_num'][i-1]
        elif renko_df['bar_num'][i]<0 and renko_df['bar_num'][i-1]<0:
            renko_df['bar_num'][i]+=renko_df['bar_num'][i-1]
    renko_df.drop_duplicates(subset='date',keep='last',inplace=True)  
    return renko_df

def renko_merge(DF):
    df=copy.deepcopy(DF)
    renko=renko_DF(df)
    df['date']=df.index
    merged_df=df.merge(renko.loc[:,['date','bar_num']],how='outer',on='date')
    merged_df['bar_num'].fillna(method='ffill',inplace=True)
    merged_df['macd']=MACD(merged_df,12,26,9)[0]
    merged_df['macd_sig']=MACD(merged_df,12,26,9)[1]
    merged_df['macd_slope']=slope(merged_df['macd'],5)
    merged_df['macd_sig_slope']=slope(merged_df['macd_sig'],5)
    return merged_df








