import numpy as np
import pandas as pd
import time
from datetime import datetime
from binance_trading_bot import visual
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter

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

def volume_analysis(client, market, TIME_FRAME_DURATION=28):
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

def analysis_visual(client, market, TIME_FRAME='1d', TIME_FRAME_DURATION=30):
    candles = get_candles(client, 
                          market,
                          TIME_FRAME, 
                          str(TIME_FRAME_DURATION)+' days ago UTC')
    volumeAnalysis = volume_analysis(client, market, TIME_FRAME_DURATION)
    f,(ax1,ax2)=plt.subplots(2,1,gridspec_kw={'height_ratios':[1,1]})
    f.set_size_inches(20,15)
    ax1.set_title('Market: '+market+\
                  ' Frame: '+TIME_FRAME+\
                  ' Duration: '+str(TIME_FRAME_DURATION)+'d', 
                  fontsize=30, 
                  y=1.03, 
                  loc='left')
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
    
def scalp_analysis(client, market):
    ticker = client.get_ticker(symbol=market)
    candles = get_candles(client, 
                          market, 
                          timeFrame='5m', 
                          timeDuration='30 minutes ago utc')
    result = pd.DataFrame(columns=['Duration', ': Buy ', ', Sell '])
    for i in [2, 1, 0]:
        result.loc[2-i] = [str(5*(i+2**i))+' mins', 
                  "{0:,.2f}".format(candles['buyQuoteVolume'].iloc[-max(3*i, 1):].sum()),
                  "{0:,.2f}".format(candles['sellQuoteVolume'].iloc[-max(3*i, 1):].sum())]
    msg = '#'+market+\
    '\nP: '+ticker['lastPrice']+\
    ' VWAP: '+ticker['weightedAvgPrice']+\
    ' V: '+"{0:,.2f}".format(float(ticker['quoteVolume']))
    for i in range(len(result)):
        msg = msg+'\n'+result[result.columns[0]].loc[i]+\
        result.columns[1]+'*'+result[result.columns[1]].loc[i]+'*'+\
        result.columns[2]+'*'+result[result.columns[2]].loc[i]+'*'
    return msg

    
    



