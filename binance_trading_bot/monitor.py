import pandas as pd
from binance_trading_bot import utilities
import time

def market_change(client):
    marketList = pd.DataFrame(client.get_products()['data'])
    parentMarketList = list(set(marketList['parentMarket'].tolist()))
    msg = '#MARKET '+time.ctime()
    for parentMarket in parentMarketList:
        baseAssetList = list(set(marketList[marketList['parentMarket']==parentMarket]['quoteAsset']))
        positiveCount = 0
        negativeCount = 0
        for baseAsset in baseAssetList:
            marketList_ = utilities.get_market_list(client, baseAsset)
            positiveCount = positiveCount+len(marketList_[marketList_['change_24h']>=0.])
            negativeCount = negativeCount+len(marketList_[marketList_['change_24h']<0.])
        msg = msg+'\n'+parentMarket+': '+str(positiveCount)+' (+) '+str(negativeCount)+' (-)'
    return msg
        