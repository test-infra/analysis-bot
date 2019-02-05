import time
import numpy as np
import pandas as pd

def get_coin_info(client, market):
    coinInfo = client.get_symbol_info(market)['filters']
    priceUnit = float(coinInfo[0]['tickSize'])
    qtyUnit = float(coinInfo[2]['stepSize'])
    return priceUnit, qtyUnit

def cancel_sell_order(client, market):
    orders = client.get_open_orders(symbol=market)
    for order in reversed(orders):
        if order['side']=='SELL':
            client.cancel_order(symbol=market, orderId=order['orderId'])
    return (time.ctime()+ ": Sell order unset: "+market)
    
def cancel_buy_order(client, market):
    orders = client.get_open_orders(symbol=market)
    for order in reversed(orders):
        if order['side']=='BUY':
            client.cancel_order(symbol=market, orderId=order['orderId'])
    return (time.ctime()+ ": Buy order unset: "+market)

def set_sell_order(client, market, profitMin=3, profitMax=13, numTransactions=10):
    priceUnit, qtyUnit = get_coin_info(client, market=market)
    coinBalance = float(client.get_asset_balance(asset=market[:-3])['free'])
    trades = client.get_my_trades(symbol=market)
    buyTrades = [trade for trade in trades if trade['isBuyer']==True]
    buyPrice = float(buyTrades[-1]['price'])
    priceMin = buyPrice*(1.00+profitMin/100)
    priceMax = buyPrice*(1.00+profitMax/100)
    priceList = np.arange(priceMin, priceMax, (priceMax-priceMin)/numTransactions)
    sellQty = coinBalance/numTransactions
    for sellPrice in priceList[:-1]:
        sellPrice = ('%.10f' % float(int(np.floor(sellPrice/priceUnit))*priceUnit)).rstrip('0').rstrip('.')
        sellQty = float(('%.10f' % float(int(np.floor(sellQty/qtyUnit))*qtyUnit)).rstrip('0').rstrip('.'))
        client.order_limit_sell(symbol=market, quantity=sellQty, price=sellPrice)
    coinBalance = float(client.get_asset_balance(asset=market[:-3])['free'])
    sellPrice = ('%.10f' % float(int(np.floor(priceList[-1]/priceUnit))*priceUnit)).rstrip('0').rstrip('.')
    sellQty = float(('%.10f' % float(int(np.floor(coinBalance/qtyUnit))*qtyUnit)).rstrip('0').rstrip('.'))
    client.order_limit_sell(symbol=market, quantity=sellQty, price=sellPrice)
    return (time.ctime()+ ": Sell order set: "+market)

def buy_order(client, market, priceMin, priceMax, numTransactions):
    cancel_buy_order(client, market)
    priceUnit, qtyUnit = get_coin_info(client, market=market)
    quoteBalance = float(client.get_asset_balance(asset=market[-3:])['free'])
    priceList = np.arange(priceMin, priceMax, (priceMax-priceMin)/numTransactions)
    buyQty = quoteBalance/numTransactions/priceMax/priceUnit
    for buyPrice in priceList:
        buyPrice = ('%.10f' % float(int(np.floor(buyPrice))*priceUnit)).rstrip('0').rstrip('.')
        buyQty = float(('%.10f' % float(int(np.floor(buyQty/qtyUnit))*qtyUnit)).rstrip('0').rstrip('.'))
        client.order_limit_buy(symbol=market, quantity=buyQty, price=buyPrice)
    return (time.ctime()+ ": Buy order set: "+market)

def sell_order(client, market, priceMin, priceMax, numTransactions):
    cancel_sell_order(client, market)
    priceUnit, qtyUnit = get_coin_info(client, market=market)
    assetBalance = float(client.get_asset_balance(asset=market[:-3])['free'])
    priceList = np.arange(priceMin, priceMax, (priceMax-priceMin)/numTransactions)
    sellQty = assetBalance/numTransactions
    for sellPrice in priceList:
        sellPrice = ('%.10f' % float(int(np.floor(sellPrice))*priceUnit)).rstrip('0').rstrip('.')
        sellQty = float(('%.10f' % float(int(np.floor(sellQty/qtyUnit))*qtyUnit)).rstrip('0').rstrip('.'))
        client.order_limit_sell(symbol=market, quantity=sellQty, price=sellPrice)
    return (time.ctime()+ ": Sell order set: "+market)






