# GCF URL: https://europe-west3-lemon-trading.cloudfunctions.net/lemon-manual-trade

# {
# 	"symbol":"IE00B3YCGJ38",
# 	"investment":1000,
# 	"side":"buy",
# 	"passphrase": "XXXXXXX"
# }


from keys_config import *
from lemon_utils import *
from lemon import api

import pandas as pd

# standard python libraries, so no need to include in GCF requirements
import datetime as dt
import random 
import time
import sys

default_investment = 1000
invoked_via = "GCF"
strategy_name = "Manual_trade"+"_invoked_"+invoked_via

def lemon_manual_trade(request):

    data = request.get_json()

    # small trick to avoid unauthorized requests to GCF
    if 'passphrase' not in data or data['passphrase'] != GCF_pass:
        return{
            "code": "error",
            "message": "You are not authorized"
        }

    client = api.create(
        market_data_api_token=LEMON_MARKET_DATA_KEY,
        trading_api_token=LEMON_PAPER_TRADING_KEY,
        env='paper'  # or env='live'
    )

    # check if xmun is open today
    message_open = check_market_open(client)
    if message_open != "open":
        return{
            "code": "error",
            "message": message_open
            }

    if 'symbol' not in data:
        return{
            "code": "error",
            "message": "No symbol to trade was provided"
        }

    if 'side' not in data:
        return{
            "code": "error",
            "message": "No side of trade was provided"
        }

    trade_symbol = data['symbol']
    trade_side = data['side']
    if 'investment' not in data:
        data['investment'] = default_investment

    try:
        investment = min(data['investment'],client.trading.account.get().results.cash_to_invest) # either max allowed either rest of cash
        latest_ask_price = pd.DataFrame(client.market_data.quotes.get_latest(isin=trade_symbol, epoch=False,sorting='asc').results).a.values[0]
        quantity_to_buy = int(investment/latest_ask_price)
        response = client.trading.orders.create(isin=trade_symbol,side=trade_side,quantity=str(quantity_to_buy),notes=strategy_name)
        new_order_id = response.results.id
        invested = response.results.estimated_price_total/10000
        client.trading.orders.activate(order_id=new_order_id) # activate sell order
        time.sleep(5)
        order_status = client.trading.orders.get_order(order_id=new_order_id).results.status
        if order_status == "executed":
            message = f'{strategy_name} {trade_side} {trade_symbol} in total for {invested}'
            inform(message)
        else: 
            inform(f"{trade_symbol} is still not traded (status = {order_status}), but continue next ...")

        return {
            "code": "trade done",
            "invested": invested
        }
    except Exception as e:
        return{
            "code": "error",
            "message": str(e)
        }
