# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 17:20:46 2020

@author: User
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd

tickers=['MMM','AXP','AAPL','BA','CAT','CVX','CSCO','KO','XOM','TSLA',
         'GE','GS','HD','INTC','IBM','JNJ','JPM','MCD','MRK','NFLX',
         'MSFT','NKE','PFE','PG','TRV','UNH','VZ','V','WMT','DIS']

financial_dir={}


for ticker in tickers:
    temp_dir={}
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)'})
    for everything in tabl:
        info=everything.find_all("div", {'class':'D(tbr)'})
        for row in info:
              if len(row.get_text(separator='|').split('|')[0:2])>1:
                  temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[1]
       
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)'})
    for everything in tabl:
        info=everything.find_all("div", {'class':'D(tbr)'})
        for row in info:
              if len(row.get_text(separator='|').split('|')[0:2])>1:
                  temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[1]
                  
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)'})
    for everything in tabl:
        info=everything.find_all("div", {'class':'D(tbr)'})
        for row in info:
              if len(row.get_text(separator='|').split('|')[0:2])>1:
                  temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[1]
                  
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'Mstart(a) Mend(a)'})
    for everything in tabl:
        info=everything.find_all("tr")
        for row in info:
            if len(row.get_text(separator='|').split('|')[0:2])>1:
                temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[-1]
              
    financial_dir[ticker]=temp_dir
    
combined_financials=pd.DataFrame(financial_dir)
combined_financials.dropna(axis=1,how='all',inplace=True)
tickers=combined_financials.columns

stats=['Operating income or loss','Market cap (intra-day)',
       'Net income available to common shareholders',
       'Net cash provided by operating activities','Capital expenditure',
       'Total current assets','Total current liabilities',
       'Net property, plant and equipment',"Total stockholders' equity",
       'Long-term debt','Forward annual dividend yield','Cash and cash equivalents',
       'Other short-term investments']
    
indx=['EBIT','MarketCap','NetIncome','CashFlowOps','Capex','CurrAsset',
      'Currliab','PPE','BookValue','TotDebt','DivYield','CashEq','ShortInves']
all_stats={}
for ticker in tickers:
    try:
        temp=combined_financials[ticker]
        ticker_stats=[]
        for stat in stats:
            ticker_stats.append(temp.loc[stat])
        all_stats['{}'.format(ticker)]=ticker_stats
    except:
        print("can't read data for ",ticker)
        
all_stats_df=pd.DataFrame(all_stats,index=indx)

all_stats_df.iloc[1,:]=[x.replace('M','E+03') for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[1,:]=[x.replace('B','E+06') for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[1,:]=[x.replace('T','E+09') for x in all_stats_df.iloc[1,:].values]
all_stats_df.iloc[-3,:]=[str(x).replace('%','E-02') for x in all_stats_df.iloc[-3,:].values]
all_stats_df[tickers]=all_stats_df[tickers].replace({',':''},regex=True)
for ticker in all_stats_df.columns:
    all_stats_df[ticker]=pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    
transpose_df=all_stats_df.transpose()
final_stats_df=pd.DataFrame()
final_stats_df['EBIT']=transpose_df['EBIT']
final_stats_df['TEV']=transpose_df['MarketCap'].fillna(0)+transpose_df['TotDebt'].fillna(0)+transpose_df['Currliab'].fillna(0)-transpose_df['CashEq'].fillna(0)-transpose_df['ShortInves'].fillna(0)
final_stats_df['EarningsYield']=final_stats_df['EBIT']/final_stats_df['TEV']
final_stats_df['FCFYield']=(transpose_df['CashFlowOps']-transpose_df['Capex'])/transpose_df['MarketCap']
final_stats_df['ROC']=transpose_df['EBIT']/(transpose_df['PPE']+transpose_df['CurrAsset']-transpose_df['Currliab'])
final_stats_df['BookToMkt']=transpose_df['BookValue']/transpose_df['MarketCap']
final_stats_df['DivYield']=transpose_df['DivYield']

final_stats_val_df=final_stats_df.loc[tickers,:]
final_stats_val_df['CombRank']=final_stats_val_df['EarningsYield'].rank(ascending=False,na_option='bottom')+final_stats_val_df['ROC'].rank(ascending=False,na_option='bottom')
final_stats_val_df['MagicFormulaRank']=final_stats_val_df['CombRank'].rank(method='first')
value_stocks=final_stats_val_df.sort_values('MagicFormulaRank').iloc[:,[2,4,8]]
print('..................')
print('value stocks based on Greenblatt Magic Formula')
print(value_stocks)

high_dividend_stocks=final_stats_val_df.sort_values('DivYield',ascending=False).iloc[:,6]
print('..................')
print('Highest dividend paying stocks')
print(high_dividend_stocks)

final_stats_df['CombRank']=final_stats_df['EarningsYield'].rank(ascending=False,method='first')+final_stats_df['ROC'].rank(ascending=False,method='first')+final_stats_df['DivYield'].rank(ascending=False,method='first')
final_stats_df['CombinedRank']=final_stats_df['CombRank'].rank(method='first')
value_high_div_stocks=final_stats_df.sort_values('CombinedRank').iloc[:,[2,4,6,8]]
print('..................')
print('Magic Formula and Dividend Yield combined')
print(value_high_div_stocks)











    
    
    
    