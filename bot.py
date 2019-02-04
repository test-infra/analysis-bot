import os
import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from binance.client import Client
import numpy as np
import pandas as pd
from binance_trading_bot import utilities, analysis, visual

MANUAL_TEXT = "@trading\_analysis\_bot is a Telegram chatbot for data-driven analytics of crypto-market with technical indicators, social sentiment, developer activities and metrics related to crossed-network on-chain transactions. The aim is to assist traders on Binance exchange.\n*Features*\n- Technical indicators: RSI, MA, BB, etc\n- Order flow: Buy vs sell, Volume profile, Limit orderbook\n- Cryptoasset indexes: Bletchley, Bitwise, CRIX\n- Cryptoasset metrics: TX vol, NVT ratio, num active addresses, num transactions\n- Social sentiment and developer activities: Twitter, Reddit, Facebook, GitHub\n- Trading sessions: New York, London, Tokyo, Sydney\n- Customized notifications: Bitfinex BTCUSD abnormal volume\n*Commands*\n- /a <coin-name-1> <market-name-2> <coin-name-3> <number-of-recent-trades> - Transactions volume versus price statistics. The argument <number-of-recent-trades> can be 500, 1000, 1500, 2000, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 25000, 30000, 35000, 40000, 45000, 50000 (can be omitted). Examples: /a qtumusdt hot bcn or /a hot npxs btcusdt 20000.\n- /t <coin-name-1> <market-2> <coin-name-3> <chart-flag> - Recent trades summary. If <chart-flag>=1, the volume vs price plot will be provided (can be omitted). Examples: /t hot bat mco 1 or /t npxs btcusdt.\n- /i <coin-name> - Coin information. Examples: /i hot or /i npxs.\n- /m - Market indexes.\n- /h - Trading sesions.\n*Supports*\nIf you don't have a crypto-trading account yet please use the these links to register to [Binance](https://www.binance.com/?ref=13339920) or [Huobi](https://www.huobi.br.com/en-us/topic/invited/?invite_code=x93k3).\nTipjar:\n- BTC: 1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq\n- ETH: 0x3915D216f9Fc6ec08f956555e84385513dE5f214\n- LTC: LX8GJkGTZFmAA7puCyVp48333iQdCN6vca\n*Contact*\nvanvuong.trinh@gmail.com"
TIME_FRAME_LIST = ['15m', '30m', '1h', '4h', '1d', '1w']
TIME_FRAME_DURATION_LIST = [1, 2, 3, 7, 30, 60]

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']
BINANCE_API_KEY = os.environ['BINANCE_API_KEY']

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def t(bot,update,args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    coin = args[-1]
    market = coin.upper()+'BTC'
    update.message.reply_text(market, parse_mode=ParseMode.MARKDOWN)
    for i in range(len(TIME_FRAME_LIST)):
        analysis.analysis_visual(client, 
                                 market, 
                                 TIME_FRAME = TIME_FRAME_LIST[i], 
                                 TIME_FRAME_DURATION = TIME_FRAME_DURATION_LIST[i])
        bot.send_photo(chat_id=update.message.chat_id, 
                       photo=open(market+'.png', 'rb'))

def manual(bot,update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text=MANUAL_TEXT, 
                     parse_mode=ParseMode.MARKDOWN, 
                     disable_web_page_preview=True)

def main():
    updater=Updater(TELEGRAM_TOKEN)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler("start", manual))
    dp.add_handler(CommandHandler("help", manual))
    dp.add_handler(CommandHandler("t", t, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
