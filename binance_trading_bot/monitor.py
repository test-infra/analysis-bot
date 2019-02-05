from binance_trading_bot import analysis
        
def active_pair_monitor(client, marketList):
    accumulateAnalysis = marketList
    n_trades = []
    buy_volume = []
    sell_volume = []
    for coin in accumulateAnalysis['symbol']:
        try:
            candles = analysis.get_candles(client, coin, '15m', '1 hour ago UTC')
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