import numpy as np
import pandas as pd
import time
from datetime import datetime
from binance_trading_bot import visual
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter

def get_trades(client, market, timeFrame, timeDuration):
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

def daily_sell_volume(client, marketList):

    analysisResult = marketList[(marketList['tradedMoney']<=200)]
    analysisResult = analysisResult[(analysisResult['tradedMoney']>0)]
    analysisResult = analysisResult.reset_index(drop=True)
    
    TIME_FRAME_DURATION = 30
    sell_volume_matrix = np.zeros((len(analysisResult['symbol']), TIME_FRAME_DURATION))
    for market_index in range(len(analysisResult['symbol'])):
        candles = get_candles(client, 
                              analysisResult['symbol'][market_index],
                              '1d', 
                              str(TIME_FRAME_DURATION)+' days ago UTC')
        for time_index in range(TIME_FRAME_DURATION):
            sell_volume_matrix.itemset((market_index, time_index),
                                       candles['sellQuoteVolume'][time_index])
    
    for time_index in range(TIME_FRAME_DURATION):
        ts = candles['open_time'][time_index]
        analysisResult[datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d')] = sell_volume_matrix[:,time_index]
    analysisResult = analysisResult.drop(columns='tradedMoney')
    analysisResult = analysisResult.set_index('symbol')
    analysisResult = analysisResult.sort_values(analysisResult.columns[-1], ascending=True)    
    
    fig, ax = plt.subplots(figsize=(30,100))
    analysisResult = analysisResult.sort_values(analysisResult.columns[-1], ascending=True)      
    sns.heatmap(analysisResult.head(100), linewidths=.5, ax=ax, cbar=False)
    plt.savefig('daily_sell_volume.png', bbox_inches='tight', format='png', dpi=300)
    
    return analysisResult

def volume_analysis(client, market, TIME_FRAME_DURATION = 28):
    
    NUM_PRICE_STEP = 20
    
    candles = get_candles(client, 
                          market,
                          '1h', 
                          str(TIME_FRAME_DURATION)+' days ago UTC')
    
    priceMin = candles['close'].min()
    priceMax = candles['close'].max()
    priceStep = (priceMax-priceMin)/NUM_PRICE_STEP
    
    volumeAnalysis = pd.DataFrame(index=np.arange(NUM_PRICE_STEP), 
                                  columns=['price_min', 'price_max', 
                                           'price', 
                                           'buy_volume',
                                           'sell_volume'])
    volumeAnalysis['price_min'] = \
    [priceMin+(i-1)*priceStep for i in np.arange(1, NUM_PRICE_STEP+1)]
    volumeAnalysis['price_max'] = \
    [priceMin+i*priceStep for i in np.arange(1, NUM_PRICE_STEP+1)]
    volumeAnalysis['price'] = \
    .5*(volumeAnalysis['price_min']+volumeAnalysis['price_max'])
    volumeAnalysis['buy_volume'] = \
    [sum(candles\
         [volumeAnalysis['price_min'][i]<=candles['close']]\
         [candles['close']<=volumeAnalysis['price_max'][i]]['buyQuoteVolume']) \
    for i in np.arange(NUM_PRICE_STEP)]
    volumeAnalysis['sell_volume'] = \
    [sum(candles\
         [volumeAnalysis['price_min'][i]<=candles['close']]\
         [candles['close']<=volumeAnalysis['price_max'][i]]['sellQuoteVolume']) \
    for i in np.arange(NUM_PRICE_STEP)]
    
    return volumeAnalysis

def analysis_visual(client, market, TIME_FRAME = '1d', TIME_FRAME_DURATION = 30):
    
    candles = get_candles(client, 
                          market,
                          TIME_FRAME, 
                          str(TIME_FRAME_DURATION)+' days ago UTC')
    volumeAnalysis = volume_analysis(client, market, TIME_FRAME_DURATION)
    
    f,(ax1,ax2)=plt.subplots(2,1,gridspec_kw={'height_ratios':[1,1]})
    f.set_size_inches(20,15)
    ax1.set_title('Market: '+market+' Time-frame: '+TIME_FRAME+' Duration: '+str(TIME_FRAME_DURATION)+'d', fontsize=25, y=1.03, loc='left')
    ax1p=ax1.twiny()
    ax1p.barh(volumeAnalysis['price'],
              volumeAnalysis['buy_volume']+volumeAnalysis['sell_volume'],
              color='gray',
              edgecolor='w',
              height=volumeAnalysis['price'][1]-volumeAnalysis['price'][0],
              align='center',
              alpha=0.25)
    ax1p.set_xticks([])
    for tic in ax1p.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
        tic.label1On = tic.label2On = False
    visual.candlestick2_ohlc(ax1, 
                             candles['open'],
                             candles['high'],
                             candles['low'],
                             candles['close'],
                             width=0.6,
                             alpha=1)
    ax1.yaxis.grid(True)
    for tic in ax1.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
        tic.label1On = tic.label2On = False
    ax1.set_xticks([])
    ax1.set_xlim(.5, len(candles))
    ax1.set_ylim(candles['low'].min(), candles['high'].max())
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
    ax1.get_yaxis().set_label_coords(-0.075,0.5) 
    ax1.set_ylabel("Volume Profile Visible Range",fontsize=20)
    visual.candlestick2_ohlc(ax2,
                             0*candles['buyQuoteVolume'],
                             candles['buyQuoteVolume']+candles['sellQuoteVolume'],
                             0*candles['buyQuoteVolume'],
                             candles['buyQuoteVolume']+candles['sellQuoteVolume'],
                             width=0.6, alpha=.35)
    visual.candlestick2_ohlc(ax2,
                             0*candles['buyQuoteVolume'],
                             candles['buyQuoteVolume'],
                             0*candles['buyQuoteVolume'],
                             candles['buyQuoteVolume'],
                             width=0.29, alpha=1, shift=-0.15)
    visual.candlestick2_ohlc(ax2,
                             candles['sellQuoteVolume'],
                             candles['sellQuoteVolume'],
                             0*candles['sellQuoteVolume'],
                             0*candles['sellQuoteVolume'],
                             width=0.29, alpha=1, shift=+0.15)
    ax2.yaxis.grid(True)
    for tic in ax2.xaxis.get_major_ticks():
        tic.tick1On = tic.tick2On = False
        tic.label1On = tic.label2On = False
    ax2.set_xticks([])
    ax2.set_xlim(.5, len(candles))
    ax2.get_yaxis().set_label_coords(-0.075,0.5) 
    ax2.set_ylabel("Buy versus Sell Quote Volume",fontsize=20)
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    f.tight_layout()
    plt.savefig(market+'.png',bbox_inches='tight')

    
    



