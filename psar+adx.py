# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 23:49:34 2021

@author: mihir
"""

import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt

ticker='^NSEI'
end=dt.datetime.today()
start=dt.datetime.today()-dt.timedelta(3650)

ohclv_data=pd.DataFrame()
ohclv_data=yf.download(ticker,start,end)
ohclv_data=ohclv_data.dropna()
def ATR(DF,n):
    df=DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-Close']=abs(df['High']-df['Close'].shift(1))
    df['L-Close']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-Close','L-Close']].max(axis=1,skipna=False)
    df['ATR']=df['TR'].rolling(n).mean()
    df2=df.copy()
    return df2

def ADX(DF,n):
    "function to calculate ADX"
    df2 = DF.copy()
    df2['TR'] = ATR(df2,n)['TR'] 
    df2['DMplus']=np.where((df2['High']-df2['High'].shift(1))>(df2['Low'].shift(1)-df2['Low']),df2['High']-df2['High'].shift(1),0)
    df2['DMplus']=np.where(df2['DMplus']<0,0,df2['DMplus'])
    df2['DMminus']=np.where((df2['Low'].shift(1)-df2['Low'])>(df2['High']-df2['High'].shift(1)),df2['Low'].shift(1)-df2['Low'],0)
    df2['DMminus']=np.where(df2['DMminus']<0,0,df2['DMminus'])
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = df2['TR'].tolist()
    DMplus = df2['DMplus'].tolist()
    DMminus = df2['DMminus'].tolist()
    for i in range(len(df2)):
        if i < n:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == n:
            TRn.append(df2['TR'].rolling(n).sum().tolist()[n])
            DMplusN.append(df2['DMplus'].rolling(n).sum().tolist()[n])
            DMminusN.append(df2['DMminus'].rolling(n).sum().tolist()[n])
        elif i > n:
            TRn.append(TRn[i-1] - (TRn[i-1]/n) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/n) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/n) + DMminus[i])
    df2['TRn'] = np.array(TRn)
    df2['DMplusN'] = np.array(DMplusN)
    df2['DMminusN'] = np.array(DMminusN)
    df2['DIplusN']=100*(df2['DMplusN']/df2['TRn'])
    df2['DIminusN']=100*(df2['DMminusN']/df2['TRn'])
    df2['DIdiff']=abs(df2['DIplusN']-df2['DIminusN'])
    df2['DIsum']=df2['DIplusN']+df2['DIminusN']
    df2['DX']=100*(df2['DIdiff']/df2['DIsum'])
    ADX = []
    DX = df2['DX'].tolist()
    for j in range(len(df2)):
        if j < 2*n-1:
            ADX.append(np.NaN)
        elif j == 2*n-1:
            ADX.append(df2['DX'][j-n+1:j+1].mean())
        elif j > 2*n-1:
            ADX.append(((n-1)*ADX[j-1] + DX[j])/n)
    df2['ADX']=np.array(ADX)
    df5=df2.copy()
    return df5
def PSAR(DF):
    df9=DF.copy()
    opening_price=df9.iloc[:,0].tolist()
    low=df9.iloc[:,2].tolist()
    high=df9.iloc[:,1].tolist()
    AF=0.02
    psar=np.zeros(len(opening_price),dtype='float')
    count=0
    ep_up=0
    ep_down=0
    for i in range(0,len(opening_price)):
        
        if i==0:
            
            if opening_price[i+10]>opening_price[i]:
                e=[]
                f=[]
                for t in range(0,10):
                    e.append(low[t])
                    f.append(high[t])                     
                psar[10]=min(e)
                ep_up=max(f)
                psar[11]=psar[10]+abs((AF*(ep_up-psar[10])))
                if high[11]>ep_up:
                    count=count+1
                    AF=0.04
                    ep_up=high[11]
            else:
                e=[]
                f=[]
                for t in range(0,10):
                    e.append(high[t])
                    f.append(low[t])
                psar[10]=max(e)
                ep_down=min(f)
                psar[11]=(psar[10]-abs((AF*(ep_down-psar[10]))))
                if low[10]<ep_down:
                    ep_down=low[10]
                    count=count+1
                    AF=0.04
                       
        elif (i>=12 and psar[i-1]<=opening_price[i-1]):
            if (count<=9 and psar[i-2]>opening_price[i-2]) :
                count=0
                AF=0.02
                ep_up=high[i]
            
            psar[i]=psar[i-1]+abs((AF*(ep_up-psar[i-1])))
                
            if(high[i]>ep_up and count<9):
                ep_up=high[i]
                count=count+1
                AF=AF+ (0.02*count)
                
            if(high[i]>ep_up):
                ep_up=high[i]
            
            if count==9:
                AF=0.2
    
                    
        elif (i>=12 and psar[i-1]>opening_price[i-1]):
            if (count<=9 and psar[i-2]<opening_price[i-2] ):
                count=0
                AF=0.02
                ep_down=low[i]
                
            psar[i]=psar[i-1]-abs((AF*(ep_down-psar[i-1])))
                
            if(low[i]<ep_down and count<9):
                ep_down=low[i]
                count=count+1
                AF=AF+ (0.02*count)
                
            if (low[i]<ep_down):

                ep_down=low[i]
            
            if count==9:
                AF=0.2
            
    psar=np.asarray(psar).reshape(len(psar),1)
    df9['PSAR']=psar
    return df9


df1=PSAR(ohclv_data)
df2=ADX(ohclv_data, 14)
x=pd.DataFrame()
x=ohclv_data.copy()
p=np.asarray(df1.iloc[-len(x):,6].values)
p=p.reshape(len(p),1)
x['PSAR']=df1.iloc[-len(p):,6].values
a=np.asarray(df2.iloc[-len(x):,17].values)
a=a.reshape(len(a),1)
x['ADX']=df2.iloc[-len(a):,17].values
a_plus=np.asarray(df2.iloc[-len(x):,12].values)
a_plus=a_plus.reshape(len(a_plus),1)
x['DI+']=df2.iloc[-len(a):,12].values
a_minus=np.asarray(df2.iloc[-len(x):,13].values)
a_minus=a_minus.reshape(len(a),1)
x['DI-']=df2.iloc[-len(a):,13].values
x=x.dropna()
p=x['PSAR'].tolist()
o=x['Open'].tolist()
psar_trend=[]
for i in range(0,len(p)):
    if p[i] < o[i]:
        psar_trend.append(1)
    else:
        psar_trend.append(0)
psar_trend=pd.DataFrame(psar_trend)
x['PSAR_trend']=psar_trend.iloc[-len(p):,0].values
adx=x['ADX'].tolist()
a_plus=x['DI+'].tolist()
a_minus=x['DI-'].tolist()
adx_trend=[]
for i in range(0,len(adx)):
    if adx[i]>15 and a_plus[i]>=a_minus[i]:
        adx_trend.append(1)
    else:
        adx_trend.append(0)
adx_trend=pd.DataFrame(adx_trend)
x['ADX_trend']=adx_trend.iloc[-len(adx):,0].values
signal=[]
adx_trend=adx_trend[0].tolist()
psar_trend=psar_trend[0].tolist()
for i in range(0,len(psar_trend)):
    if psar_trend[i]==1 and adx_trend[i]==1:
        signal.append(1)
    elif psar_trend[i]==0 and adx_trend[i]==0:
        signal.append(-1)
    else:
        signal.append(0)
signal=pd.DataFrame(signal)
x['SIGNAL']=signal.iloc[-len(signal):,0].values

