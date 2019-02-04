import time
import numpy as np
import pandas as pd

def get_coin_info(client, market):
    coinInfo = client.get_symbol_info(market)['filters']
    priceUnit = float(coinInfo[0]['tickSize'])
    qtyUnit = float(coinInfo[2]['stepSize'])
    return priceUnit, qtyUnit

def set_buy_order(client, market, buyPrice):
    priceUnit, qtyUnit = get_coin_info(client, market=market)
    btcBalance = float(client.get_asset_balance(asset='BTC')['free'])
    buyQty = min(0.05*btcBalance, 0.0011)/buyPrice
    buyPrice = ('%.10f' % float(int(np.floor(buyPrice/priceUnit))*priceUnit)).rstrip('0').rstrip('.')
    buyQty = float(('%.10f' % float(int(np.floor(buyQty/qtyUnit))*qtyUnit)).rstrip('0').rstrip('.'))
    client.order_limit_buy(symbol=market, quantity=buyQty, price=buyPrice)
    return (time.ctime()+ ": Buy order set: "+market)
   
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

def account_balance(client):
    balances = pd.DataFrame(client.get_account()['balances'])
    balances = balances[(pd.to_numeric(balances['free'])+pd.to_numeric(balances['locked'])>=1e-6)]
    balances['baseQty'] = balances['free']+balances['locked']
    return balances



