import logging
import math
import configparser
import spreadsheet
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['binance']['api_key']
api_secret = config['binance']['api_secret']

client = Client(api_key, api_secret)

# Testnet setting
# Create a client for the Testnet
#client = Client(api_key, api_secret, testnet=True)
# Base URL for the Testnet
#client.API_URL = 'https://testnet.binance.vision/api'

# Rows to extracts from the spreadsheet
n = int(config['spreadsheet']['start'])
m = int(config['spreadsheet']['finish'])

def buy_token(symbol, quantity):
    try:
        order = client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        logging.info(f"Order successful! Order details: {order}")
    except Exception as e:
        logging.error(f"An error occurred while buying: {e}")

def lot_size(symbol):
    try:
        exchange_info = client.get_symbol_info(symbol)
        for f in exchange_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                minQty = float(f['minQty'])
                stepSize = float(f['stepSize'])
                logging.info(f"Lot Size for {symbol}: minimum quantity is {minQty} with a step of {stepSize}")
                return minQty
    except Exception as e:
        logging.error(f"Could not retrieve lot size for {symbol}: {e}")
    return None

def get_last_percentage():
    try:
        with open('percentages.txt', 'r') as file:
            lines = file.readlines()
            if lines:
                return lines[-1].strip()
    except FileNotFoundError:
        return None
    return None

def get_total_balance_in_usdt():
    account_info = client.get_account()
    total_usdt = 0.0

    for asset in account_info['balances']:
        if float(asset['free']) > 0:
            if asset['asset'] == 'USDT':
                total_usdt += float(asset['free'])
            else:
                symbol = asset['asset'] + 'USDT'
                try:
                    ticker = client.get_symbol_ticker(symbol=symbol)
                    price_in_usdt = float(ticker['price'])
                    total_usdt += price_in_usdt * float(asset['free'])
                except Exception as e:
                    logging.error(f"Could not get price for {symbol}: {e}")
    return total_usdt

def getpriceofpairs(n, m):
    crypto_pairs = list(spreadsheet.get_crypto_pairs(n, m))
    asset_prices = {}
    account_info = client.get_account()
    balances = account_info['balances']

    for balance in balances:
        try:
            asset = balance['asset']
            if asset == 'USDT' or asset == 'USDTUSDT':
                continue
            if asset in crypto_pairs:
                symbol = f"{asset}USDT"
                price_info = client.get_symbol_ticker(symbol=symbol)
                current_price = float(price_info['price'])
                asset_prices[asset] = current_price 
        except Exception as e:
            logging.error(f"Error fetching wallet balance for {asset}: {e}")
    return asset_prices

def get_balance():
    account_info = client.get_account()
    total_usdt = 0.0

    for asset in account_info['balances']:
        if float(asset['free']) > 0:
            logging.info(f"Asset: {asset['asset']}, Free: {asset['free']}, Locked: {asset['locked']}")
            try:
                if asset['asset'] == "USDT":
                    total_usdt += float(asset['free'])
                    logging.info(f"{asset['asset']}: {asset['free']} USDT\n")
                else:
                    symbol = asset['asset'] + 'USDT'
                    ticker = client.get_symbol_ticker(symbol=symbol)
                    price_in_usdt = float(ticker['price'])
                    a = price_in_usdt * float(asset['free'])
                    total_usdt += a
                    logging.info(f"You have {a} USDT of {asset['asset']}")
                logging.info(f"Total balance in USDT: {total_usdt}")
            except Exception as e:
                logging.error(f"Could not get price for {symbol}: {e}")
    return total_usdt

def get_wallet_balance():
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        for balance in balances:
            if float(balance['free']) > 0:
                logging.info(f"Asset: {balance['asset']}, Free: {balance['free']}, Locked: {balance['locked']}")
            yield balance
    except Exception as e:
        logging.error(f"Error fetching wallet balance: {e}")

def sell_token(symbol, quantity):
    try:
        order = client.create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        logging.info(f"Order successful! Order details: {order}")
    except Exception as e:
        logging.error(f"An error occurred while selling: {e}")

def sell_all():
    balances = get_wallet_balance()  # Get wallet balances from the API
    for balance in balances: 
        # Skip USDT and USDTUSDT pairs
        if balance['asset'] == 'USDT' or balance['asset'] == 'USDTUSDT':
            continue
        
        if float(balance['free']) > 0:
            try:
                symbol = f"{balance['asset']}USDT"

                calcul_lot_size = round(1 /lot_size(symbol))
                logging.info(f"Lot size for {symbol}: {lot_size(symbol)}")

                # Get the current price for the trading pair
                price_info = client.get_symbol_ticker(symbol=symbol)
                quantity = math.floor(float(balance['free']) * calcul_lot_size) / calcul_lot_size # Round at 3 decimals
                sell_token(symbol, quantity)

            except Exception as e:
                print(f"Error for {balance['asset']}: {e}")

# Sell all cryptos for USDT
sell_all()

# Get total USDT balance
total_balance = get_total_balance_in_usdt()
logging.info(f"Total balance in USDT: {total_balance}")

prices = getpriceofpairs(n, m)
#print("Asset Prices:", prices)

for pair in spreadsheet.get_crypto_pairs(n, m):
    # Get the last percent of the strategy
    last_percent = int(get_last_percentage())

    if last_percent == 0:
        cleaned_value = 0

    elif last_percent == 25:
        cleaned_value = spreadsheet.generate_sheet(n, m)[pair][0].replace('%', '').replace(',', '.').strip()
    
    elif last_percent == 50:
        cleaned_value = spreadsheet.generate_sheet(n, m)[pair][1].replace('%', '').replace(',', '.').strip()

    elif last_percent == 75:
        cleaned_value = spreadsheet.generate_sheet(n, m)[pair][2].replace('%', '').replace(',', '.').strip()

    elif last_percent == 100:
        cleaned_value = spreadsheet.generate_sheet(n, m)[pair][3].replace('%', '').replace(',', '.').strip()
    else:
        logging.info(f"Wrong % !")

    logging.info(f"% of {pair} is {cleaned_value}%")

    if pair == 'USDT':
        continue

    if float(cleaned_value) > 0 and pair in prices:
        symbol = f"{pair}USDT"
        calcul_lot_size = round(1 /float(lot_size(symbol)))
        logging.info(f"Lot size for {symbol}: {lot_size(symbol)}")
        logging.info(f"Price of {pair} is {prices[pair]}")

        amount_to_spend = total_balance * (float(cleaned_value)/100)
        raw_quantity = amount_to_spend / prices[pair]
        rounded_down = math.floor(raw_quantity * calcul_lot_size) / calcul_lot_size
        buy_token(symbol, rounded_down)
        logging.info(f"Buying {amount_to_spend} USDT of {symbol} or {rounded_down} {pair}")

get_balance()