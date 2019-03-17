import pandas as pd
from binance_trading_bot import utilities
import time

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

def stop_hunt(client, stophuntRatio, TIME_FRAME, TIME_FRAME_DURATION):
    marketList = utilities.get_market_list(client, 'BTC')
    marketList['stop_hunt'] = 1.
    for i in marketList.index:
        market = marketList.at[i, 'symbol']
        candles = utilities.get_candles(client, market, TIME_FRAME, TIME_FRAME_DURATION)
        candle = candles[candles['low']<stophuntRatio*candles['close']]
        if len(candle)>=1:
            marketList.at[i, 'stop_hunt'] = (candle['low']/candle['close']).min()
    candidateList = marketList[marketList['stop_hunt']<1.]
    candidateList = candidateList.sort_values('stop_hunt', ascending=True)['symbol'].tolist()
    msg = '#STOPHUNT\n'
    msg = msg+' '.join([item[:-3] for item in candidateList])
    return msg

        