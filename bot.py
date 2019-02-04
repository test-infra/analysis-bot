import os
import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from binance.client import Client
import numpy as np
import pandas as pd
from binance_trading_bot import utilities, analysis, visual
from config import *

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']
BINANCE_API_KEY = os.environ['BINANCE_API_KEY']

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def t(bot,update,args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    coin = args
    market = coin.upper()+'BTC'
    for i in range(len(TIME_FRAME_LIST)):
        analysis.analysis_visual(client, 
                                 market, 
                                 TIME_FRAME = TIME_FRAME_LIST[i], 
                                 TIME_FRAME_DURATION = TIME_FRAME_DURATION_LIST[i])
        bot.send_photo(chat_id=update.message.chat_id, 
                       photo=open(str(market)+'.png', 'rb'))

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
