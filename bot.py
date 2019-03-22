import os
import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from binance.client import Client
from binance_trading_bot import utilities, analysis, monitor

MANUAL_TEXT = """Data-driven analytics of crypto-market on Binance.
*Commands*
- /t <market> : volatility and supply analysis.
Usage: /t qtumusdt or /t btt xlmusdt bttbnb.
- /s <asset> : asset analysis.
Usage: /s qtum or /s btt fet.
- /m : market statistics.
Usage: /m.
*Supports*
Start trading on [Binance](https://www.binance.com/?ref=13339920), [Huobi](https://www.huobi.br.com/en-us/topic/invited/?invite_code=x93k3) or [Coinbase](https://www.coinbase.com/join/581a706d01bc8b00dd1d1737).
Use the [Brave](https://brave.com/ken335) privacy browser to earn BAT token.
BTC tipjar: [1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq](1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq).
*Contact*
@tjeuphi
*Website*
[https://kenhtaichinh.herokuapp.com](https://kenhtaichinh.herokuapp.com).
 """

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']
BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
TELEGRAM_ADMIN_USERNAME = os.environ['TELEGRAM_ADMIN_USERNAME']

userList = [TELEGRAM_ADMIN_USERNAME]

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def x(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        for market in args:
            market = market.upper()
            try:
                TIME_FRAME_STEP = [args[-3]]
                TIME_FRAME = [args[-2]]
                TIME_FRAME_DURATION = [args[-1].replace('_', ' ')]
                analysis.analysis_visual(client, 
                                         market, 
                                         TIME_FRAME_STEP, 
                                         TIME_FRAME, 
                                         TIME_FRAME_DURATION)
            except Exception:
                TIME_FRAME_STEP = ['15m']
                TIME_FRAME = ['1h']
                TIME_FRAME_DURATION = ['3 days ago UTC']
                analysis.analysis_visual(client, 
                                         market, 
                                         TIME_FRAME_STEP, 
                                         TIME_FRAME, 
                                         TIME_FRAME_DURATION)
            bot.send_photo(chat_id=update.message.chat_id, 
                       photo=open('img/'+market+'.png', 'rb'))

def t(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        for market in args:
            market = market.upper()
            TIME_FRAME_STEP = ['15m', '15m', '15m']
            TIME_FRAME = ['1w', '1d', '4h']
            TIME_FRAME_DURATION = ['365 days ago UTC', '90 days ago UTC', '14 days ago UTC']
            try:
                analysis.analysis_visual(client, 
                                         market, 
                                         TIME_FRAME_STEP, 
                                         TIME_FRAME, 
                                         TIME_FRAME_DURATION)
            except Exception:
                market = market+'BTC'
                analysis.analysis_visual(client, 
                                         market, 
                                         TIME_FRAME_STEP, 
                                         TIME_FRAME, 
                                         TIME_FRAME_DURATION)
            bot.send_photo(chat_id=update.message.chat_id, 
                       photo=open('img/'+market+'.png', 'rb'))

def s(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        for asset in args:
            asset = asset.upper()
            msg = analysis.asset_analysis(client, asset)
            update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

def m(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        msg = monitor.market_change(client)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        
def admin(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username)==TELEGRAM_ADMIN_USERNAME:
        global userList
        option = args[0]
        if option=='user':
            msg = ' '.join(str(user) for user in userList)
        if option=='add':
            for user in args[1:]:
                userList.append(user)
            userList = list(set(userList))
        if option=='remove':
            for user in args[1:]:
                try:
                    userList.remove(user)
                except Exception:
                    pass
        update.message.reply_text(msg)

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
    dp.add_handler(CommandHandler("m", m))
    dp.add_handler(CommandHandler("x", x, pass_args=True))
    dp.add_handler(CommandHandler("t", t, pass_args=True))
    dp.add_handler(CommandHandler("s", s, pass_args=True))
    dp.add_handler(CommandHandler("admin", admin, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()