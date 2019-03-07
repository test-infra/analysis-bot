import os
import telegram
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from binance.client import Client
from binance_trading_bot import utilities, analysis, monitor, news

MANUAL_TEXT = """A Telegram chatbot for data-driven analytics of crypto-market on Binance.
Homepage: [https://kenhtaichinh.herokuapp.com](https://kenhtaichinh.herokuapp.com).
*Features*
- Altcoin analysis: Demand versus supply imbalance.
- Market movement: Statistics, Indexes (Bletchley, CRIX).
- Bitcoin metrics: NVT (Ratio/Signal), MVRV (Z-Score), Network momentum.
- Newsflow: Curated articles, Project profiles.
*Commands*
- /t <market>
Usage: /t qtumusdt or /t btt xlmusdt bttbnb.
- /s <asset>
Usage: /s qtum or /s btt fet.
- /a <change-24h-lb> <change-24h-ub> 
Two last arguments can be omitted. 
Usage: /a or /a 3 8 or /a -5 5.
- /x <minute-count> <vol-lb> <vol-ub>
Three last arguments can be omitted. 
Usage: /x or /x 15 75 1000.
- /m 
Usage: /m.
- /n
Usage: /n.
*Supports*
Start trading on [Binance](https://www.binance.com/?ref=13339920), [Huobi](https://www.huobi.br.com/en-us/topic/invited/?invite_code=x93k3) or [Coinbase](https://www.coinbase.com/join/581a706d01bc8b00dd1d1737).
Use the [Brave](https://brave.com/ken335) privacy browser to earn BAT token.
BTC tipjar: [1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq](1DrEMhMP5rAytKyKXRzc6szTcUX8bZzZgq).
*Contact*
@tjeuphi
_Disclaimer: Only available for registered users._
 """

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']
BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
TELEGRAM_ADMIN_USERNAME = os.environ['TELEGRAM_ADMIN_USERNAME']

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

userList = [TELEGRAM_ADMIN_USERNAME]

def a(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        try:
            change_24h_lb = float(args[-2])
            change_24h_ub = float(args[-1])
        except Exception:
            change_24h_lb = -2
            change_24h_ub = +10
        marketList = utilities.get_market_list(client, 'BTC')
        marketList = marketList[marketList['change_24h']>=change_24h_lb]
        marketList = marketList[marketList['change_24h']<=change_24h_ub]
        TIME_FRAME_STEP = ['15m', '15m', '15m']
        TIME_FRAME = ['1d', '4h', '1h']
        TIME_FRAME_DURATION = ['60 days ago UTC', '14 days ago UTC', '5 days ago UTC']
        for market in marketList['symbol']:
            try:
                analysis.analysis_visual(client, 
                                         market, 
                                         TIME_FRAME_STEP, 
                                         TIME_FRAME, 
                                         TIME_FRAME_DURATION)
                bot.send_photo(chat_id=update.message.chat_id, 
                               photo=open('img/'+market+'.png', 'rb'))
            except Exception:
                pass

def t(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        for market in args:
            market = market.upper()
            TIME_FRAME_STEP = ['15m', '15m', '15m']
            TIME_FRAME = ['1d', '4h', '1h']
            TIME_FRAME_DURATION = ['90 days ago UTC', '14 days ago UTC', '5 days ago UTC']
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
        
def x(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        try:
            MIN_COUNT = int(args[-3])
            VOL_LB = float(args[-2])
            VOL_UB = float(args[-1])
        except:
            MIN_COUNT = 10
            VOL_LB = 30
            VOL_UB = 1000
        accumulateAnalysis, msg = monitor.active_trading(client, MIN_COUNT, VOL_LB, VOL_UB)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        
def n(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, 
                         action=telegram.ChatAction.TYPING)
    if str(update.message.from_user.username) in userList:
        msg = news.newsflow()
        update.message.reply_text(msg, 
                                  parse_mode=ParseMode.MARKDOWN,
                                  disable_web_page_preview=True)
        
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
    dp.add_handler(CommandHandler("n", n))
    dp.add_handler(CommandHandler("a", a, pass_args=True))
    dp.add_handler(CommandHandler("t", t, pass_args=True))
    dp.add_handler(CommandHandler("s", s, pass_args=True))
    dp.add_handler(CommandHandler("x", x, pass_args=True))
    dp.add_handler(CommandHandler("admin", admin, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
