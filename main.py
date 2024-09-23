import requests
import asyncio
import json
import os
import hashlib
import hmac
import time
import datetime


api_key = 'IN2t13uftIUkZoOfCgbcQCYTaoeEEf'
api_secret = '3mgt1SR3Fi5Qa1HALTQTw340kGQgxtHNub3Wqm2ekmVE0TLSMyloZYbDZFsU'

def generate_signature(method, endpoint, payload):
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + payload
    message = bytes(signature_data, 'utf-8')
    secret = bytes(api_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest(), timestamp

def get_time_stamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970,1,1)
    return str(int((d - epoch).total_seconds()))

BOT_TOKEN = '6903959874:AAG6PR1Uq44pLISk3olhHUyl53Npk9ogKqk'
CHAT_ID = '311396636'

async def fetch_profile_data():    
    send_message("😀Sell Algo Live😀")

async def place_target_order(order_type, side, order_product, order_size, stop_order_type, stop_price):
    payload = {
        "order_type": order_type,
        "side": side,
        "product_id": int(order_product),
        "stop_order_type": stop_order_type,
        "stop_price": stop_price,
        "reduce_only": False,
        "stop_trigger_method": "mark_price",
        "size": order_size
    }
    print(payload)
    
    method = 'POST'
    endpoint = '/v2/orders'
    payload_str = json.dumps(payload)
    signature, timestamp = generate_signature(method, endpoint, payload_str)
    timestamp = get_time_stamp()

    headers = {
        'api-key': api_key,
        'timestamp': timestamp,
        'signature': signature,
        'User-Agent': 'rest-client',
        'Content-Type': 'application/json'
    }

    response = requests.post('https://cdn.india.deltaex.org/v2/orders', json=payload, headers=headers)
    
    if response.status_code == 200:
        message = f"😀New Order:\n" \
                  f"Order Type: {payload['order_type']}\n" \
                  f"Side: {payload['side']}\n" \
                  f"Product ID: {payload['product_id']}\n" \
                  f"Stop Order Type: {payload['stop_order_type']}\n" \
                  f"Stop Price: {payload['stop_price']}\n" \
                  f"Reduce Only: {payload['reduce_only']}\n" \
                  f"Stop Trigger Method: {payload['stop_trigger_method']}\n" \
                  f"Size: {payload['size']}😀"
        send_message(message)
    else:
        print("Failed to place order. Status code:", response.status_code)

async def place_order(order_type, side, order_product_id, order_size, stop_order_type, target_value):
    payload = {
        "order_type": order_type,
        "side": side,
        "product_id": int(order_product_id),
        "reduce_only": False,     
        "size": order_size
    }

    method = 'POST'
    endpoint = '/v2/orders'
    payload_str = json.dumps(payload)
    signature, timestamp = generate_signature(method, endpoint, payload_str)
    timestamp = get_time_stamp()

    headers = {
        'api-key': api_key,
        'timestamp': timestamp,
        'signature': signature,
        'User-Agent': 'rest-client',
        'Content-Type': 'application/json'
    }

    response = requests.post('https://cdn.india.deltaex.org/v2/orders', json=payload, headers=headers)
    
    if response.status_code == 200:
        message = f"😀New Order:\n" \
                  f"Order Type: {payload['order_type']}\n" \
                  f"Side: {payload['side']}\n" \
                  f"Product ID: {payload['product_id']}\n" \
                  f"Reduce Only: {'Yes' if payload['reduce_only'] else 'No'}\n" \
                  f"Size: {payload['size']}😀"
        send_message(message)
        print("Order placed successfully.")
        await place_target_order("market_order", "buy", order_product_id, 1, "take_profit_order", target_value)
    else:
        print("Failed to place order. Status code:", response.status_code)

async def fetch_position_data():
    payload = ''
    method = 'GET'
    endpoint = '/v2/positions/margined'
    payload_str = json.dumps(payload)
    signature, timestamp = generate_signature(method, endpoint, payload)

    headers = {
        'api-key': api_key,
        'timestamp': timestamp,
        'signature': signature,
        'User-Agent': 'rest-client',
        'Content-Type': 'application/json'
    }

    r = requests.get('https://cdn.india.deltaex.org/v2/positions/margined', headers=headers)
    position_data = r.json()

    for result in position_data["result"]:
        product_id = result["product_id"]
        product_symbol = result["product_symbol"]
        realized_cashflow = result["realized_cashflow"]
        realized_pnl = result["realized_pnl"]
        size = result["size"]
        unrealized_pnl = result["unrealized_pnl"]
        entry_price = result["entry_price"]
        mark_price = result["mark_price"]

        print("Product ID:", product_id, "Product Symbol:", product_symbol)
        
        percentage = int(size) * 0.75
        price_value = float(entry_price) - (float(entry_price) * (percentage / 100))
        target = round((float(mark_price) * 2 / 100 - float(mark_price)) * 20) / 20
        target_value = abs(target)

        message = f"Symbol: {product_symbol}\n" \
                  f"Size: {size}\n" \
                  f"Unrealized PnL: {round((float(unrealized_pnl)), 2)}\n" \
                  f"Entry Price: {round((float(entry_price)), 2)}\n" \
                  f"Next_Entry: {round((float(price_value)), 2)}\n" \
                  f"Mark Price: {round((float(mark_price)), 2)}\n"
        send_message(message)

        if float(mark_price) > price_value:
            print("Ready to sell")
            await place_order("market_order", "sell", product_id, 1, 0, target_value)

def send_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {'chat_id': CHAT_ID, 'text': message}

    response = requests.post(url, json=params)
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print(f'Failed to send message. Error: {response.status_code} - {response.text}')

def get_public_ip():
    try:
        # Fetch public IP address from an external service
        response = requests.get('https://api.ipify.org?format=json')
        ip_data = response.json()
        ip_address = ip_data.get('ip')
        print(ip_address)
        return ip_address
    except requests.RequestException as e:
        print(f"Error fetching IP address: {e}")
        return None

async def main():
    try:
        ip_address = get_public_ip()
        if ip_address:
            print(f"Public IP Address: {ip_address}")
        else:
            print("Failed to retrieve IP address.")
        
        profile_task = asyncio.create_task(fetch_profile_data())
        position_task = asyncio.create_task(fetch_position_data())
        await asyncio.gather(position_task, profile_task)
    except Exception as e:
        print(f"An error occurred: {e}")

        

# Run the main coroutine once
asyncio.run(main())
