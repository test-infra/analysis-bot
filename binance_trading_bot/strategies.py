from binance_trading_bot import order

import time

def buy_multiple_coin(client, marketList, dipList):
    marketNumbers = len(marketList)
    marketIndex = -1    
    while 1:
        print("\n")
        marketIndex = marketIndex+1
        if marketIndex>marketNumbers-1: 
            marketIndex = 0
        market = marketList[marketIndex]
        buyPrice = dipList[marketIndex]
        order.set_buy_order(client, market, buyPrice)
        time.sleep(2)
        order.cancel_buy_order(client, market)