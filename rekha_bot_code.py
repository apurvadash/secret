
from telegram import *
from telegram.ext import *
import time
import requests
import json

#----------------------------------------------------------->

reader = open('info.txt','r')
info = reader.read()
reader.close()

info = info.split(',')

user_id = info[1]
password = info[2]
twofa = info[3]
multiplier = int(info[4])

#-----------------------------------------------------------> market order function

def mkt(strike,quantity,direction):
    
    order_payload = {
    'variety':'regular',
    'exchange':'NFO',
    'tradingsymbol':strike,
    'transaction_type':direction,
    'order_type':'MARKET',
    'quantity':str(quantity),
    'product':'MIS',
    'user_id':user_id
    }

    response = s.post(order_url,data=order_payload)
    print(response.text)
    
    return response

#-----------------------------------------------------------> sl-m order function

def slm(strike,quantity,trigger_price,direction):

    order_payload = {
    'variety':'regular',
    'exchange':'NFO',
    'tradingsymbol':strike,
    'transaction_type':direction,
    'order_type':'SL-M',
    'quantity':str(quantity),
    'trigger_price':str(trigger_price),
    'product':'MIS',
    'user_id':user_id
    }

    response = s.post(order_url,data=order_payload)
    print(response.text)

    return

#----------------------------------------------------------->

s = requests.Session()

url_1 = 'https://kite.zerodha.com/api/login'
payload_1={'user_id':user_id,'password':password}
response_1 = s.post(url_1,data=payload_1)
request_id = response_1.json()['data']['request_id']

url_2 = 'https://kite.zerodha.com/api/twofa'
payload_2={'user_id':user_id,'request_id':request_id,'twofa_value':twofa}
response_2 = s.post(url_2,data=payload_2)
enctoken = response_2.cookies['enctoken']

s.headers.update({'authorization':'enctoken '+str(enctoken)})

order_url = 'https://kite.zerodha.com/oms/orders/regular'

#----------------------------------------------------------->

bot_token = info[0]

bot = Bot(bot_token)

def echo(update: Update, context: CallbackContext):

    msg = update.channel_post.text

    if 'entry' in msg:
        
        trade_data = msg.split(',')
        strike = trade_data[1]
        stop = float(trade_data[2])
        quantity = multiplier*50

        mkt(strike,quantity,'SELL')

        time.sleep(2)
        
        slm(strike,quantity,stop,'BUY')

    if 'exit' in msg:
        mkt(strike,quantity,'BUY')

updater = Updater(bot_token,use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()