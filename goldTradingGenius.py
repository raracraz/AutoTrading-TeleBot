import configparser
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater
import logging
import time
import re
import MetaTrader5 as mt5

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read the token and your user ID from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

my_username = config.get('Telegram', 'my_username')
my_user_id = int(config.get('Telegram', 'my_user_id'))  # Add your_user_id to your config file

token = config.get('TradingBot', 'token')

mt5_login = int(config.get('MetaTrader', 'login'))
mt5_password = config.get('MetaTrader', 'password')
mt5_server = config.get('MetaTrader', 'server')

# Initialize MT5 connection with login credentials
# if not mt5.initialize(login=mt5_login, password=mt5_password, server=mt5_server):
#     print("initialize() failed, error code =",mt5.last_error())
#     quit()

# Initialize MT5 connection without login credentials
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# Now you're connected. You can fetch account information, place trades, etc.
print(mt5.account_info())

def handle_message(update: Update, context: CallbackContext) -> None:
    text = None
    
    # Check if the update contains a regular message
    if update.message:
        text = update.message.text
    # Check if the update contains a channel post
    elif update.channel_post:
        text = update.channel_post.text
    
    # If no text was found, return
    if not text:
        return
    
    if text.startswith("🔷") or text.startswith("XAUUSD") or text.startswith("GBPJPY"):
        print(f"Received matching message: {text}")
        context.bot.send_message(my_user_id, f"Received a new matching message: {text}")
        info = extract_order_info(text)
        
        # Check for TP targets in order: tp3, tp2, tp1
        tp_target = info.get('tp3') or info.get('tp2') or info.get('tp1')
        print(f"TP target: {tp_target}")
        
        if tp_target:
            place_market_order(info['symbol'], info['order_type'], 0.03, info['sl'], tp_target)
        else:
            print("No TP target found!")
        
        print(info)

def extract_order_info(text: str) -> dict:
    results = {}

    # Extract the symbol (e.g., XAUUSD, GBPJPY)
    symbol_match = re.search(r'(\w+)', text)
    if symbol_match:
        results['symbol'] = symbol_match.group(1)

    # Extract order type (Buy/Sell)
    order_type_match = re.search(r'(BUY|SELL)', text, re.IGNORECASE)
    if order_type_match:
        results['order_type'] = order_type_match.group(1).upper()

    # Extract order price and format to three decimal places
    price_match = re.search(r'(BUY|SELL)\s+([\d\.]+)(?:\/[\d\.]+)?', text, re.IGNORECASE)
    if price_match:
        results['order_price'] = float(format(float(price_match.group(2)), ".3f"))

    # Extract SL value and format to three decimal places
    sl_match = re.search(r'SL\s*([\d\.]+)', text)
    if sl_match:
        results['sl'] = float(format(float(sl_match.group(1)), ".3f"))

    # Extract TP values and format each to three decimal places
    tp_matches = re.findall(r'TP\s*([\d\.]+)', text)
    for index, tp_value in enumerate(tp_matches, start=1):
        key = f"tp{index}"
        results[key] = float(format(float(tp_value), ".3f"))

    return results


# def place_limit_order(symbol, action, volume, price, sl, tp):
#     current_price = mt5.symbol_info(symbol).bid  # or .ask, depending on your needs

#     if action == "BUY":
#         if price > current_price:  # If the BUY limit is above the current price
#             order_type = mt5.ORDER_TYPE_BUY_STOP
#         else:
#             order_type = mt5.ORDER_TYPE_BUY_LIMIT
#     elif action == "SELL":
#         if price < current_price:  # If the SELL limit is below the current price
#             order_type = mt5.ORDER_TYPE_SELL_STOP
#         else:
#             order_type = mt5.ORDER_TYPE_SELL_LIMIT
#     else:
#         print(f"Unknown action: {action}")
#         return
    
#     # Create the request
#     request = {
#         "action": mt5.TRADE_ACTION_PENDING,
#         "symbol": symbol,
#         "volume": volume,
#         "type": order_type,
#         "price": price,
#         "sl": sl,
#         "tp": tp,
#         "magic": 123456,  # Magic number, can be any identifier you choose
#         "comment": "python script open",  # Comment on the order
#         "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
#         "type_filling": mt5.ORDER_FILLING_RETURN,
#     }

def place_market_order(symbol, action, volume, sl, tp):
    if action == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
    elif action == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        print(f"Unknown action: {action}")
        return
    
    # Create the request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,  # This is for immediate execution
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "sl": sl,
        "tp": tp,
        "magic": 123456,  # Magic number, can be any identifier you choose
        "comment": "python script open",  # Comment on the order
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the request
    result = mt5.order_send(request)
    
    if result is None:
        print("Failed to send order. No response received.")
        error = mt5.last_error()
        print("Error in order_send(): ", error)
        return

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to send order. Error: {result.comment}")
        return
    print(f"Order successfully placed with ticket {result.order}")
    return result.order


#     # Send the request
#     result = mt5.order_send(request)
    
#     if result is None:
#         print("Failed to send order. No response received.")
#         error = mt5.last_error()
#         print("Error in order_send(): ", error)
#         return

#     if result.retcode != mt5.TRADE_RETCODE_DONE:
#         print(f"Failed to send order. Error: {result.comment}")
#         return
#     print(f"Order successfully placed with ticket {result.order}")
#     return result.order


# Create an updater and pass your bot's token
updater = Updater(token=token)

# On each message, call the 'handle_message' function
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot with a retry mechanism
max_retries = 5
retry_delay = 5  # Start with a 5-second delay

for retry in range(max_retries):
    try:
        updater.start_polling()
        print("Bot started polling...")
        break  # If successful, break out of the loop
    except Exception as e:
        if retry < max_retries - 1:  # Don't print the last error message, as it will exit after that
            print(f"Error occurred while starting the bot (Attempt {retry + 1}/{max_retries}): {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Double the delay for the next retry
        else:
            print(f"Error occurred and max retries reached: {e}")
            exit(1)

updater.idle()
