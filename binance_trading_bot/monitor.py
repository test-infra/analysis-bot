import numpy as np
import pandas as pd
from datetime import datetime
from binance_trading_bot import utilities, visual, analysis
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter
import time
        
def active_trading(client, MIN_COUNT=10, VOL_LB=30, VOL_UB=1000):
    marketList = pd.DataFrame(client.get_products()['data'])
    marketList = marketList[marketList['marketName']=='BTC']
    marketList = marketList[marketList['tradedMoney']<=VOL_UB]
    marketList = marketList[marketList['tradedMoney']>=VOL_LB]
    n_trades = []
    buy_volume = []
    sell_volume = []
    for coin in marketList['symbol']:
        try:
            candles = utilities.get_candles(client, coin, '1m', '1 hour ago UTC')
            n_trades.append(sum(candles['n_trades'].iloc[-MIN_COUNT:]))
            buy_volume.append("{0:,.2f}".format(sum(candles['buyQuoteVolume'].iloc[-MIN_COUNT:])))
            sell_volume.append("{0:,.2f}".format(sum(candles['sellQuoteVolume'].iloc[-MIN_COUNT:])))
        except Exception:
            n_trades.append(0)
            buy_volume.append(0)
            sell_volume.append(0)            
    marketList['n_trades'] = n_trades
    marketList['buy_volume'] = buy_volume
    marketList['sell_volume'] = sell_volume
    marketList = marketList[(marketList['n_trades']>=100)]
    marketList = marketList.sort_values('n_trades', ascending=False)
    accumulateAnalysis = pd.DataFrame()
    accumulateAnalysis['symbol'] = marketList['symbol']
    accumulateAnalysis['n_trades'] = marketList['n_trades']
    accumulateAnalysis['buy_volume'] = marketList['buy_volume']
    accumulateAnalysis['sell_volume'] = marketList['sell_volume']
    msg = '#MARKET Last '+str(MIN_COUNT)+'min'
    for i in accumulateAnalysis.index:
        msg = msg+'\n'+accumulateAnalysis.at[i, 'symbol'][:-3]+\
        ' ('+str(accumulateAnalysis.at[i, 'n_trades'])+') '+\
        ' Buy *'+accumulateAnalysis.at[i, 'buy_volume']+'* '+\
        ' Sell *'+accumulateAnalysis.at[i, 'sell_volume']+'*'
        if float(accumulateAnalysis.at[i, 'buy_volume'])>=float(accumulateAnalysis.at[i, 'sell_volume']):
            msg = msg+' (+)'
        else:
            msg = msg+' (-)'
    return accumulateAnalysis, msg

def market_change(client):
    marketList = pd.DataFrame(client.get_products()['data'])
    parentMarketList = list(set(marketList['parentMarket'].tolist()))
    msg = '#MARKET '
    for parentMarket in parentMarketList:
        baseAssetList = list(set(marketList[marketList['parentMarket']==parentMarket]['quoteAsset']))
        positiveCount = 0
        negativeCount = 0
        neutralCount = 0
        for baseAsset in baseAssetList:
            marketList_ = utilities.get_market_list(client, baseAsset)
            positiveCount = positiveCount+len(marketList_[marketList_['change_24h']>=1.])
            negativeCount = negativeCount+len(marketList_[marketList_['change_24h']<=-1.])
            neutralCount = neutralCount+len(marketList_)-len(marketList_[marketList_['change_24h']>=1.])-len(marketList_[marketList_['change_24h']<=-1.])
        msg = msg+'\n'+parentMarket+': '+str(positiveCount)+' (+) '+str(negativeCount)+' (-) '+str(neutralCount)+' (0)'
    msg = msg+'\n'+time.ctime()
    return msg
        