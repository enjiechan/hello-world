# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 17:49:03 2020

@author: User
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd

tickers=['MMM','AXP','AAPL','BA','CAT','CVX','CSCO','KO','XOM','TSLA',
         'GE','GS','HD','INTC','IBM','JNJ','JPM','MCD','MRK','NFLX',
         'MSFT','NKE','PFE','PG','TRV','UNH','VZ','V','WMT','DIS']

financial_dir_cy={}
financial_dir_py={}
financial_dir_py2={}

for ticker in tickers:
    print('scraping financial statement data for ',ticker)
    temp_dir={}
    temp_dir2={}
    temp_dir3={}
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
                temp_dir2[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[2]
                temp_dir3[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[3]
                
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)'})
    for everything in tabl:
        info=everything.find_all("div", {'class':'D(tbr)'})
        for row in info:
            if len(row.get_text(separator='|').split('|')[0:2])>1:
                  temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[2]
                  temp_dir2[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[3]
                  temp_dir3[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[4]
                  
    url='https://sg.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
    page=requests.get(url)
    page_content=page.content
    soup=BeautifulSoup(page_content, 'html.parser')
    tabl=soup.find_all("div", {'class':'M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)'})
    for everything in tabl:
        info=everything.find_all("div", {'class':'D(tbr)'})
        for row in info:
              if len(row.get_text(separator='|').split('|')[0:2])>1:
                  temp_dir[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[2]
                  temp_dir2[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[3]
                  temp_dir3[row.get_text(separator='|').split('|')[0]]=row.get_text(separator='|').split('|')[4]
                  
    financial_dir_cy[ticker]=temp_dir
    financial_dir_py[ticker]=temp_dir2
    financial_dir_py2[ticker]=temp_dir3
    
combined_financials_cy=pd.DataFrame(financial_dir_cy)
combined_financials_cy.dropna(axis=1,how='all',inplace=True)
combined_financials_py=pd.DataFrame(financial_dir_py)
combined_financials_py.dropna(axis=1,how='all',inplace=True)
combined_financials_py2=pd.DataFrame(financial_dir_py2)
combined_financials_py2.dropna(axis=1,how='all',inplace=True)
tickers=combined_financials_cy.columns

stats=['Net income available to common shareholders','Total assets',
       'Operating cash flow','Long-term debt','Other long-term liabilities',
       'Total current assets','Total current liabilities','Common stock',
       'Total revenue','Gross profit']

indx=['NetIncome','TotAssets','CashFlowOps','LTDebt','OtherLTDebt','CurrAssets',
      'CurrLiab','CommStock','TotRevenue','GrossProfit']

def info_filter(df,stats,indx):
    tickers=df.columns
    all_stats={}
    for ticker in tickers:
        try:
            temp=df[ticker]
            ticker_stats=[]
            for stat in stats:
                ticker_stats.append(temp.loc[stat])
            all_stats['{}'.format(ticker)]=ticker_stats
        except:
            print("can't read data for ",ticker)
    
    all_stats_df=pd.DataFrame(all_stats,index=indx)
    
    all_stats_df[tickers]=all_stats_df[tickers].replace({',':''},regex=True)
    for ticker in all_stats_df.columns:
        all_stats_df[ticker]=pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    return all_stats_df

#haha=info_filter(combined_financials_cy,stats,indx)

def piotroski_f(df_cy,df_py,df_py2):
    f_score={}
    tickers=df_cy.columns
    for ticker in tickers:
        ROA_FS=int(df_cy.loc['NetIncome',ticker]/((df_cy.loc['TotAssets',ticker]+df_py.loc['TotAssets',ticker])/2)>0)
        CFO_FS=int(df_cy.loc['CashFlowOps',ticker]>0)
        ROA_D_FS=int(df_cy.loc['NetIncome',ticker]/((df_cy.loc['TotAssets',ticker]+df_py.loc['TotAssets',ticker])/2)>df_py.loc['NetIncome',ticker]/((df_py.loc['TotAssets',ticker]+df_py2.loc['TotAssets',ticker])/2))
        CFO_ROA_FS=int(df_cy.loc['CashFlowOps',ticker]/df_cy.loc['TotAssets',ticker]>df_cy.loc['NetIncome',ticker]/df_cy.loc['TotAssets',ticker])
        LTD_FS=int((df_cy.loc['LTDebt',ticker]+df_cy.loc['OtherLTDebt',ticker])<(df_py.loc['LTDebt',ticker]+df_py.loc['OtherLTDebt',ticker]))
        CR_FS=int((df_cy.loc['CurrAssets',ticker]/df_cy.loc['CurrLiab',ticker])>(df_py.loc['CurrAssets',ticker]/df_py.loc['CurrLiab',ticker]))
        DILUTION_FS=int(df_cy.loc['CommStock',ticker]<=df_py.loc['CommStock',ticker])
        GM_FS=int((df_cy.loc['GrossProfit',ticker]/df_cy.loc['TotRevenue',ticker])>(df_py.loc['GrossProfit',ticker]/df_py.loc['TotRevenue',ticker]))
        ATO_FS=int((df_cy.loc['TotRevenue',ticker]/((df_cy.loc['TotAssets',ticker]+df_py.loc['TotAssets',ticker])/2))>(df_py.loc['TotRevenue',ticker]/((df_py.loc['TotAssets',ticker]+df_py2.loc['TotAssets',ticker])/2)))
        f_score[ticker]=[ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df=pd.DataFrame(f_score,index=['PosROA','PosCFO','ROAChange','Accruals','Leverage','Liquidity','Dilution','GM','ATO'])
    return f_score_df

transformed_df_cy=info_filter(combined_financials_cy,stats,indx)
transformed_df_py=info_filter(combined_financials_py,stats,indx)
transformed_df_py2=info_filter(combined_financials_py2,stats,indx)

f_score_df=piotroski_f(transformed_df_cy,transformed_df_py,transformed_df_py2)
scorecard=f_score_df.sum().sort_values(ascending=False)

            
    





