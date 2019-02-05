import pandas as pd

def get_market_list(client):
    marketList = pd.DataFrame(client.get_products()['data'])
    marketList = marketList[(marketList['quoteAsset']=='BTC')]
    marketList = marketList[['symbol', 'tradedMoney']]
    return marketList




     