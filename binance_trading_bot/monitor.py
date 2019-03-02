import numpy as np
import pandas as pd
from datetime import datetime
from binance_trading_bot import utilities, visual, analysis
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter
import time
        
def active_trading(client, marketList):
    accumulateAnalysis = marketList
    n_trades = []
    buy_volume = []
    sell_volume = []
    for coin in accumulateAnalysis['symbol']:
        try:
            candles = utilities.get_candles(client, coin, '1m', '1 hour ago UTC')
            n_trades.append(sum(candles['n_trades'].iloc[-5:]))
            buy_volume.append(sum(candles['buyQuoteVolume'].iloc[-5:]))
            sell_volume.append(sum(candles['sellQuoteVolume'].iloc[-5:]))
        except Exception:
            n_trades.append(0)
            buy_volume.append(0)
            sell_volume.append(0)            
    accumulateAnalysis['n_trades'] = n_trades
    accumulateAnalysis['buy_volume'] = buy_volume
    accumulateAnalysis['sell_volume'] = sell_volume
    accumulateAnalysis = accumulateAnalysis[(accumulateAnalysis['n_trades']>=100)]
    accumulateAnalysis = accumulateAnalysis.set_index('symbol')
    accumulateAnalysis = accumulateAnalysis.drop(['tradedMoney', 'n_trades_24h', 'change_24h'], 1)
    accumulateAnalysis = accumulateAnalysis.sort_values('n_trades', 
                                                        ascending=False)
    return accumulateAnalysis

def market_change(client):
    marketList = pd.DataFrame(client.get_products()['data'])
    parentMarketList = list(set(marketList['parentMarket'].tolist()))
    msg = '#MARKET '
    for parentMarket in parentMarketList:
        baseAssetList = list(set(marketList[marketList['parentMarket']==parentMarket]['quoteAsset']))
        positiveCount = 0
        negativeCount = 0
        for baseAsset in baseAssetList:
            marketList_ = utilities.get_market_list(client, baseAsset)
            positiveCount = positiveCount+len(marketList_[marketList_['change_24h']>=0.])
            negativeCount = negativeCount+len(marketList_[marketList_['change_24h']<0.])
        msg = msg+'\n'+parentMarket+': '+str(positiveCount)+' (+) '+str(negativeCount)+' (-)'
    msg = msg+'\n'+time.ctime()
    return msg
        