import numpy as np
import pandas as pd

def get_trades(client, market, timeDuration, timeFrame):
    klines = client.get_historical_klines(symbol=market, 
                                          interval=timeFrame, 
                                          start_str=timeDuration)
    n_transactions = sum([item[8] for item in klines])
    toId = client.get_historical_trades(symbol=market, limit=1)[0]['id']
    listId = np.arange(toId-n_transactions+1, toId-10,500)
    trades = []
    for fromId in listId:
        trades = trades+client.get_historical_trades(symbol=market, 
                                                     fromId=str(fromId))
    trades = pd.DataFrame(trades)
    trades['price'] = pd.to_numeric(trades['price'])
    trades['qty'] = pd.to_numeric(trades['qty'])
    trades['value'] = trades['price']*trades['qty']
    return trades

def get_candles(client, market, timeFrame, timeDuration):
    klines = client.get_historical_klines(symbol=market, 
                                          interval=timeFrame, 
                                          start_str=timeDuration)
    klines = pd.DataFrame(klines)    
    candles = pd.DataFrame()  
    candles['open_time'] = klines[0]
    candles['close_time'] = klines[6]
    candles['n_trades'] = klines[8]
    candles['open'] = pd.to_numeric(klines[1])
    candles['high'] = pd.to_numeric(klines[2])
    candles['low'] = pd.to_numeric(klines[3])
    candles['close'] = pd.to_numeric(klines[4])
    candles['assetVolume'] = pd.to_numeric(klines[5])
    candles['buyAssetVolume'] = pd.to_numeric(klines[9])
    candles['sellAssetVolume'] = candles['assetVolume']-candles['buyAssetVolume']
    candles['quoteVolume'] = pd.to_numeric(klines[7])
    candles['buyQuoteVolume'] = pd.to_numeric(klines[10])
    candles['sellQuoteVolume'] = candles['quoteVolume']-candles['buyQuoteVolume']
    return candles






     