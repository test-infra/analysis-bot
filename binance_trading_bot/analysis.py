import numpy as np
import pandas as pd
import time
from datetime import datetime
from binance_trading_bot import utilities, visual
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter
from pandas_talib import *

def supply_analysis(client, 
                    marketList, 
                    DAILY_SELL_VOLUME_THRESHOLD=30,
                    TIME_FRAME_DURATION=30):
    analysisResult = marketList[(marketList['tradedMoney']<=DAILY_SELL_VOLUME_THRESHOLD)]
    analysisResult = analysisResult[(analysisResult['tradedMoney']>0)]
    analysisResult = analysisResult.reset_index(drop=True)
    sell_volume_matrix = np.zeros((len(analysisResult['symbol']), TIME_FRAME_DURATION))
    for market_index in range(len(analysisResult['symbol'])):
        candles = utilities.get_candles(client, 
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
    fig, ax = plt.subplots(figsize=(30,20))
    analysisResult = analysisResult.sort_values(analysisResult.columns[-1], ascending=True)      
    sns.heatmap(analysisResult.head(20), linewidths=.5, ax=ax, cbar=False)
    plt.savefig('img/daily_sell_volume.png', bbox_inches='tight', format='png', dpi=300) 
    return analysisResult

def volume_analysis(client, market, TIME_FRAME_DURATION):
    NUM_PRICE_STEP = 20
    candles = utilities.get_candles(client, 
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

def analysis_visual(client, market):
    f,ax = plt.subplots(2, 3, gridspec_kw={'height_ratios':[1, 1]})
    f.set_size_inches(60,15)
    TIME_FRAME = ['1d', '4h', '1h']
    TIME_FRAME_DURATION = [30, 7, 3]
    for i in [0, 1, 2]:
        candles = utilities.get_candles(client, 
                                        market,
                                        TIME_FRAME[i], 
                                        str(TIME_FRAME_DURATION[i])+' days ago UTC')
        volumeAnalysis = volume_analysis(client, market, TIME_FRAME_DURATION)
        ax[0, i].set_title(market+' '+TIME_FRAME[i].upper()+'/'+str(TIME_FRAME_DURATION[i])+'D', fontsize=30, y=1.03, loc='left')
        axt = ax[0, i].twiny()
        axt.barh(volumeAnalysis['price'],
                 volumeAnalysis['buy_volume']+volumeAnalysis['sell_volume'],
                 color='gray',
                 edgecolor='w',
                 height=volumeAnalysis['price'][1]-volumeAnalysis['price'][0],
                 align='center',
                 alpha=0.25)
        axt.set_xticks([])
        for tic in axt.xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        visual.candlestick2_ohlc(ax[0, i], 
                                 candles['open'],
                                 candles['high'],
                                 candles['low'],
                                 candles['close'],
                                 width=0.6, alpha=1)
        ax[0, i].yaxis.grid(True)
        for tic in ax[0, i].xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        ax[0, i].set_xticks([])
        ax[0, i].set_xlim(.5, len(candles))
        ax[0, i].set_ylim(candles['low'].min(), candles['high'].max())
        ax[0, i].yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
        ax[0, i].get_yaxis().set_label_coords(-0.075,0.5) 
        visual.candlestick2_ohlc(ax[1, i],
                                 0*candles['buyQuoteVolume'],
                                 candles['buyQuoteVolume']+candles['sellQuoteVolume'],
                                 0*candles['buyQuoteVolume'],
                                 candles['buyQuoteVolume']+candles['sellQuoteVolume'],
                                 width=0.6, alpha=.35)
        visual.candlestick2_ohlc(ax[1, i],
                                 0*candles['buyQuoteVolume'],
                                 candles['buyQuoteVolume'],
                                 0*candles['buyQuoteVolume'],
                                 candles['buyQuoteVolume'],
                                 width=0.29, alpha=1, shift=-0.15)
        visual.candlestick2_ohlc(ax[1, i],
                                 candles['sellQuoteVolume'],
                                 candles['sellQuoteVolume'],
                                 0*candles['sellQuoteVolume'],
                                 0*candles['sellQuoteVolume'],
                                 width=0.29, alpha=1, shift=+0.15)
        ax[1, i].yaxis.grid(True)
        for tic in ax[1, i].xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        ax[1, i].set_xticks([])
        ax[1, i].set_xlim(.5, len(candles))
        ax[1, i].get_yaxis().set_label_coords(-0.075,0.5) 
        ax[1, i].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        axt = ax[1, i].twinx()
        analysisResult = pd.DataFrame()
        candles['OBV'] = candles['buyQuoteVolume']-candles['sellQuoteVolume']
        candles['OBV'] = candles['OBV'].cumsum()
        analysisResult['Close'] = candles['OBV']
        axt.plot(MA(analysisResult, 3)['MA_3'], linewidth=4, color='violet', label='MA(3)')
        axt.plot(MA(analysisResult, 8)['MA_8'], linewidth=4, color='orange', label='MA(8)')
        axt.plot(candles['OBV'], linewidth=4, color='indigo', label='Demand-Supply')
        for tic in axt.yaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        if i==0:
            ax[0, i].set_ylabel("Volume Profile Visible Range",fontsize=20)
            ax[1, i].set_ylabel("Buy versus Sell Quote Volume",fontsize=20)
            plt.legend(loc='upper left', prop={'size': 20})
    f.tight_layout()
    plt.savefig('img/'+market+'.png',bbox_inches='tight')
    
def scalp_analysis(client, market):
    ticker = client.get_ticker(symbol=market)
    candles = utilities.get_candles(client, 
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



    
    



