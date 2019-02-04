import os
import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from binance.client import Client
import numpy as np
import pandas as pd
from binance_trading_bot import utilities, analysis, visual

MANUAL_TEXT = """@trading\_analysis\_bot is a Telegram chatbot for data-driven
 analytics of crypto-market with technical indicators, social sentiment, 
 developer activities and metrics related to crossed-network on-chain 
 transactions. The aim is to assist traders on Binance exchange.
 \n*Features*
 \n- Technical indicators: MA, BB, Ichimoku, VRVP ...
 \n- Order flow: Buy vs sell volume, Trades, Limit order book
 \n- Indexes: Bletchley, Bitwise, CRIX
 \n- Metrics: TX vol, NVT ratio, num active addresses, num transactions
 \n- Sentiment and development: Twitter, Reddit, Facebook, GitHub
 \n- Trading sessions: New York, London, Tokyo, Sydney
 \n- Customized notifications
 \n*Commands*\n- /t <market-name-1> <market-name-2> <time-frame> <num-day> - 
 Transactions volume versus price statistics. 
 The argument <time-frame> and <num-day> can be omitted. 
 Examples: /t qtumusdt bttbnb or /a bttbtc xlmusdt 4h 30
 \n- /m - Market indexes.
 \n- /h - Trading sesions.
 \n*Supports*
 \nIf you don't have an account yet please use the these links to register to
 [Binance](https://www.binance.com/?ref=13339920) or
 [Huobi](https://www.huobi.br.com/en-us/topic/invited/?invite_code=x93k3).
 \nTipjar:
 \n- BTC: 1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq
 \n- ETH: 0x3915D216f9Fc6ec08f956555e84385513dE5f214
 \n- LTC: LX8GJkGTZFmAA7puCyVp48333iQdCN6vca
 \n*Contact*\nvanvuong.trinh@gmail.com"""

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']
BINANCE_API_KEY = os.environ['BINANCE_API_KEY']

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def t(bot,update,args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    for market in args:
        market = market.upper()
        msg = analysis.scalp_analysis(client, market)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        try:
            TIME_FRAME = args[1]
            TIME_FRAME_DURATION = int(args[2])
            analysis.analysis_visual(client, 
                                     market, 
                                     TIME_FRAME, 
                                     TIME_FRAME_DURATION)
            bot.send_photo(chat_id=update.message.chat_id, 
                           photo=open(market+'.png', 'rb'))
        except Exception:
            pass

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
