import numpy as np
import pandas as pd
from datetime import datetime
from binance_trading_bot import utilities, visual
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('classic')
from matplotlib.ticker import FormatStrFormatter

def volume_analysis(client, market, TIME_FRAME_STEP, TIME_FRAME_DURATION):
    NUM_PRICE_STEP = 20
    candles = utilities.get_candles(client, 
                                    market,
                                    TIME_FRAME_STEP, 
                                    TIME_FRAME_DURATION)
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

def analysis_visual(client, market, TIME_FRAME_STEP, TIME_FRAME, TIME_FRAME_DURATION):
    f,ax = plt.subplots(2, len(TIME_FRAME), gridspec_kw={'height_ratios':[1, 1]})
    f.set_size_inches(20*len(TIME_FRAME),20)
    for i in np.arange(len(TIME_FRAME)):
        candles = utilities.get_candles(client, 
                                        market,
                                        TIME_FRAME[i], 
                                        TIME_FRAME_DURATION[i])
        volumeAnalysis = volume_analysis(client, market, TIME_FRAME_STEP[i], TIME_FRAME_DURATION[i])
        try:
            ax1 = ax[0, i]
            ax2 = ax[1, i]
        except Exception:
            ax1 = ax[0]
            ax2 = ax[1]    
        axt = ax1.twiny()
        axt.barh(volumeAnalysis['price'],
                 volumeAnalysis['sell_volume'],
                 color='gray',
                 edgecolor='w',
                 height=volumeAnalysis['price'][1]-volumeAnalysis['price'][0],
                 align='center',
                 alpha=0.25)
        axt.set_xticks([])
        for tic in axt.xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        visual.candlestick2_ohlc(ax1, 
                                 candles['open'],
                                 candles['high'],
                                 candles['low'],
                                 candles['close'],
                                 width=0.6, alpha=1)
        ax1.plot(candles['close'].rolling(7).mean(), linewidth=4, color='violet', label='Moving Average (7)')
        ax1.plot(candles['close'].rolling(13).mean(), linewidth=4, color='orange', label='Moving Average (13)')
        ax1.yaxis.grid(True)
        for tic in ax1.xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        ax1.set_xticks([])
        ax1.set_xlim(.5, len(candles))
        ax1.set_ylim(candles['low'].min(), candles['high'].max())
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
        ax1.get_yaxis().set_label_coords(-0.075,0.5) 
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
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        axt = ax2.twinx()
        candles['OBV'] = candles['buyQuoteVolume']-candles['sellQuoteVolume']
        candles['OBV'] = candles['OBV'].cumsum()
        axt.plot(candles['OBV'].rolling(7).mean(), linewidth=4, color='violet', label='Simple Moving Average (7)')
        axt.plot(candles['OBV'].rolling(13).mean(), linewidth=4, color='orange', label='Simple Moving Average (13)')
        axt.plot(candles['OBV'], linewidth=4, color='indigo', label='Demand and Supply Balance')
        for tic in axt.yaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
            tic.label1On = tic.label2On = False
        ax2.get_xaxis().set_label_coords(0.5, -0.025) 
        ax2.set_xlabel(TIME_FRAME[i].upper(), fontsize=20)
        if i==0:
            ax1.set_ylabel("Sell Volume Profile Visible Range",fontsize=20)
            ax2.set_ylabel("Buy versus Sell Quote Volume",fontsize=20)
            plt.legend(loc='upper left', prop={'size': 20})
            ax1.set_title(market, fontsize=40, y=1.03, loc='left')
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



