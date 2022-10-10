# GCF URL: https://europe-west3-lemon-trading.cloudfunctions.net/buy_random_ETF_constit
# request = {"passphrase": "XXXX"}

from keys_config import *
from lemon_utils import *
from lemon import api
import lemon_universes

from datetime import datetime
import pandas as pd
import random # standard python library
import time # standard python library
import sys # standard python library

client = api.create(
    market_data_api_token=LEMON_MARKET_DATA_KEY,
    trading_api_token=LEMON_PAPER_TRADING_KEY,
    env='paper'  # or env='live'
)

focus = lemon_universes.guru
max_investment_per_position = 1000
max_items = 10 # I don't want to have more than 10 stocks in pf
stop_loss = 0.95
invoked_via = "GCF"
strategy_name = "GURU"+"_"+str(max_investment_per_position)+"_"+str(max_items)+"_invoked_"+invoked_via

def buy_random_ETF_constit(request):

    data = request.get_json()

    # small trick to avoid unauthorized requests to GCF
    if 'passphrase' not in data or data['passphrase'] != GCF_pass:
        return{
            "code": "error",
            "message": "You are not authorized"
        }

    # Check if exchange is open
    current_positions_df = pd.DataFrame(client.trading.positions.get().results) # DF of current positions
    current_positions_df['PL'] = current_positions_df.estimated_price/current_positions_df.buy_price_avg # Checking unprofitable
    current_isins = current_positions_df['isin'].to_list() # even if we sell unprofitable, I don't want to buy them immediately again
    unprofitable_isins_sell = current_positions_df[current_positions_df.PL<stop_loss]['isin'].to_list() 
    # maybe also to check how long in the unprofitable position already ?
    side = 'buy'

    if len(unprofitable_isins_sell)<1:
        inform('All positions are in profit. Decide discreationary if you want to sell smth')
        sys.exit()

    inform(f'{unprofitable_isins_sell} items from portfolio should be sold. Starting ...')
    for stock in unprofitable_isins_sell: # selling unprofitable positions
        quantity_to_sell = current_positions_df[current_positions_df['isin']==stock].quantity.values[0]
        title_to_sell = current_positions_df[current_positions_df['isin']==stock].isin_title.values[0]
        sell_response = client.trading.orders.create(isin=stock,side=side,quantity=str(quantity_to_sell),notes=strategy_name+"_sell") # sell order, idempotency="XXXXX"
        sell_order_id = sell_response.results.id
        client.trading.orders.activate(order_id=sell_order_id) # activate sell order
        print(f"Waiting on execution for selling {quantity_to_sell} stocks of {title_to_sell}...")
        time.sleep(7)
        order_status = client.trading.orders.get_order(order_id=sell_order_id).results.status
        if order_status == "executed":
            message = f'{strategy_name} {side} {title_to_sell} in total for {investment}'
            inform(message)
        else: 
            print(f"{title_to_sell} is still not sold (status = {order_status}), but continue next ...")

    orders = client.trading.orders.get().results
    open_sell_orders = {order.id for order in orders if order.status != "executed" }
    if len(open_sell_orders) >0:
        print(f'There are still {len(open_sell_orders)} not executed orders')
    else:
        print(f'All sell orders were executed')

    num_to_buy = max_items - len(set(current_isins) - set(unprofitable_isins_sell))
    if num_to_buy<1:
        print(f'There are already {current_isins} stocks in portfolio. You need to sell smth')
        sys.exit()

    # Mapping between Gettex ticker and NYSE ticker is done via ISINs as it seems they are identical
    # I need also filter for some KPI, e.g. momentum, fundamentals or member of an ETF?
    
    focus_xmun = [x for x in focus if x in lemon_universes.xmun_universe] # isins from strategy, which are traded on xmun
    available_isins =  list(set(focus_xmun) - set(current_isins) - set(unprofitable_isins_sell)) # buy only what is not in pf
    isins_buy = random.choices(available_isins,k=num_to_buy)
    side = 'buy'

    for stock in isins_buy:
        investment = min(max_investment_per_position,client.trading.account.get().results.cash_to_invest) # either max allowed either rest of cash
        # here could be risk that the previous order hasn't been excuted yet
        latest_ask_price = pd.DataFrame(client.market_data.quotes.get_latest(isin=stock, epoch=False,sorting='asc').results).a.values[0]
        quantity_to_buy = int(investment/latest_ask_price)
        buy_response = client.trading.orders.create(isin=stock,side=side,quantity=quantity_to_buy,notes=strategy_name+"_buy") # sell order, idempotency="XXXXX"
        buy_order_id = buy_response.results.id
        client.trading.orders.activate(order_id=buy_order_id) # activate sell order
        print(f"Waiting on execution for buying {quantity_to_buy} stocks of {stock}...")
        time.sleep(7)
        order_status = client.trading.orders.get_order(order_id=buy_order_id).results.status
        if order_status == "executed":
            message = f'{strategy_name} {side} {stock} in total for {investment}'
            inform(message)
        else: 
            print(f"{stock} is still not bought (status = {order_status}), but continue next ...")

    current_positions_df = pd.DataFrame(client.trading.positions.get().results) # DF of current positions
    current_positions_df.rename(columns={'isin_title': 'Name', 'estimated_price_total': 'Value'}, inplace=True)
    current_positions_df['Value'] = current_positions_df['Value'] / 1000000
    current_positions_df['PL'] = (current_positions_df.estimated_price/current_positions_df.buy_price_avg) # Checking unprofitable
    interesting_collums = ['isin', 'Name','Value','PL']      
    current_positions_df = current_positions_df[interesting_collums]
    current_positions_df = current_positions_df.round({'PL': 2, 'Value': 1})

    send_email(strategy_name, current_positions_df)
