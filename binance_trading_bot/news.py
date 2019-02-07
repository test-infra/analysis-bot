from six.moves import urllib
import json
import pandas as pd

def news():
    url = "https://data.messari.io/api/v1/news"
    news = pd.DataFrame(json.load(urllib.request.urlopen(url))['data'])
    news = news[['title', 'url']]
    msg = '*Newsflow*'
    for i in range(len(news)):
        msg = msg+'\n'+news['title'].iat[i]+'\n'+news['url'].iat[i]
    return msg


