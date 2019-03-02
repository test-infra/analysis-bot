import numpy as np
import pandas as pd
import time

def get_market_list(client, *args):
    marketList = pd.DataFrame(client.get_products()['data'])
    if len(args)>0:
        quoteBase = args[0]
        marketList = marketList[marketList['quoteAsset']==quoteBase]
    marketList = marketList[['symbol', 'tradedMoney']]
    tickers = pd.DataFrame(client.get_ticker())
    tickers['priceChangePercent'] = pd.to_numeric(tickers['priceChangePercent'])
    tickerList = pd.DataFrame()
    tickerList['symbol'] = tickers['symbol']
    tickerList['n_trades_24h'] = tickers['count']
    tickerList['change_24h'] = tickers['priceChangePercent']
    marketList = pd.merge(marketList, tickerList, on='symbol')
    marketList = marketList.sort_values('change_24h', ascending=False) 
    return marketList

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

def get_order_book(client, market):
    bids = pd.DataFrame(client.get_order_book(symbol=market)['bids']).drop(columns=2)
    bids.columns = ['price', 'baseQty']
    bids = bids.apply(pd.to_numeric, errors='coerce')
    bids['quoteValue'] = bids['price']*bids['baseQty']
    bids['cumsum'] = bids['quoteValue'].cumsum()
    bids = bids.drop(columns=['baseQty', 'quoteValue'])
    asks = pd.DataFrame(client.get_order_book(symbol=market)['asks']).drop(columns=2)
    asks.columns = ['price', 'baseQty']
    asks = asks.apply(pd.to_numeric, errors='coerce')
    asks['quoteValue'] = asks['price']*asks['baseQty']
    asks['cumsum'] = asks['quoteValue'].cumsum()
    asks = asks.drop(columns=['baseQty', 'quoteValue'])
    lob = bids.append(asks, ignore_index=True)
    lob = lob.sort_values('price', ascending=True)
    lob.columns = ['price', time.ctime()]
    return lob




     