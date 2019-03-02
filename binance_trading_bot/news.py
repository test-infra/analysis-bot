from six.moves import urllib
import json

def newsflow():
    url = "https://data.messari.io/api/v1/news"
    data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))['data']
    msg = '*Newsflow*'
    for item in data:
        try:
            msg = msg+'\n'+item['title']+' ([url]('+item['url']+'))'
        except Exception:
            pass
    return msg