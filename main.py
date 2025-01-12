import requests
import asyncio
import json
import os
import hashlib
import hmac
import time
import datetime
from decimal import Decimal

api_key = 'WqLMWdFHsYrWt5dHELyBkZXzVw54s4'
api_secret = 'ux8394Juap4ZzvA3oXPYkgVaR4MAza6BwsKWLTOVCFNcv5wgPi3HAb0Pqirm'

BOT_TOKEN = '7003653511:AAGkx1MumC07d4gJh9zb9l7dCqDfyeTHjtY'
CHAT_ID = '311396636'

def generate_signature(method, endpoint, payload):
    timestamp = str(int(time.time()))
    signature_data = method + timestamp + endpoint + payload
    message = bytes(signature_data, 'utf-8')
    secret = bytes(api_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest(), timestamp

def get_time_stamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970, 1, 1)
    return str(int((d - epoch).total_seconds()))

def send_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {'chat_id': CHAT_ID, 'text': message}

    response = requests.post(url, json=params)
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print(f'Failed to send message. Error: {response.status_code} - {response.text}')

async def fetch_profile_data():
    print("Fetching profile data...")
    send_message("Algo Start")    

async def fetch_position_data():
    print("Fetching position data...")
    
    payload = ''
    method = 'GET'
    endpoint = '/v2/positions/margined'
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
    send_message("Algo Live")

    for result in position_data.get("result", []):
        product_symbol = result.get("product_symbol")
        size = result.get("size")
        unrealized_pnl = result.get("unrealized_pnl")
        entry_price = result.get("entry_price")
        mark_price = result.get("mark_price")

        message = f"Symbol: {product_symbol}\n" \
                  f"Size: {size}\n" \
                  f"Unrealized PnL: {unrealized_pnl}\n" \
                  f"Entry Price: {entry_price}\n" \
                  f"Mark Price: {mark_price}\n"
        
        print(message)

async def main():
    try:
        # Perform only one iteration of tasks
        await fetch_profile_data()
        await fetch_position_data()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Script finished execution.")

if __name__ == "__main__":
    asyncio.run(main())
