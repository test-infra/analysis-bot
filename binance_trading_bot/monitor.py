from binance_trading_bot import utilities, analysis
        
def active_pair_monitor(client, marketList):
    accumulateAnalysis = marketList
    n_trades = []
    buy_volume = []
    sell_volume = []
    for coin in accumulateAnalysis['symbol']:
        try:
            candles = utilities.get_candles(client, coin, '15m', '1 hour ago UTC')
            n_trades.append(candles['n_trades'].iloc[-1])
            buy_volume.append(candles['buyQuoteVolume'].iloc[-1])
            sell_volume.append(candles['sellQuoteVolume'].iloc[-1])
        except Exception:
            n_trades.append(0)
            buy_volume.append(0)
            sell_volume.append(0)            
    accumulateAnalysis['n_trades'] = n_trades
    accumulateAnalysis['buy_volume'] = buy_volume
    accumulateAnalysis['sell_volume'] = sell_volume
    accumulateAnalysis = accumulateAnalysis[(accumulateAnalysis['n_trades']>=100)]
    accumulateAnalysis = accumulateAnalysis.drop(columns='tradedMoney')
    accumulateAnalysis = accumulateAnalysis.set_index('symbol')
    accumulateAnalysis = accumulateAnalysis.sort_values('n_trades', 
                                                        ascending=False)
    return accumulateAnalysis

def positive_divergence(client, marketList):
    for market in marketList:
        candles = utilities.get_candles(client, market, '1d', '14 days ago UTC')
        candles['OBV'] = candles['buyQuoteVolume']-candles['sellQuoteVolume']
        candles['OBV'] = candles['OBV'].cumsum()
        if candles['OBV'].iat[-1]>=candles['OBV'].iat[-2]:
            analysis.analysis_visual(client, market)