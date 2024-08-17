import telegram
import configparser
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater
import logging
import time
import re
import MetaTrader5 as mt5

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read the token and your user ID from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

my_username = config.get('Telegram', 'my_username')
my_user_id = int(config.get('Telegram', 'my_user_id'))
token = config.get('TradingBot', 'token')
lot_size = float(config.get('Settings', 'lot_size'))

def initialize_bot():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    print(mt5.account_info())

def handle_message(update: Update, context: CallbackContext) -> None:
    text = None
    if update.message:
        text = update.message.text
    elif update.channel_post:
        text = update.channel_post.text
    if not text:
        return

    if re.search(r'\s?([A-Z]{6})\s', text):
        print(f"Received matching message: {text}")
        context.bot.send_message(my_user_id, f"Received a new matching message: \n\n{text}")
        info = extract_order_info(text)
        
        if 'order_price' not in info:
            print("Order price not found!")
            return

        tp_values = [value for key, value in info.items() if key.startswith("tp")]
        if not tp_values:
            print("No TP targets found!")
            return

        volume_per_tp = float(lot_size) / len(tp_values)
        i = 1
        msg = []

        for tp in tp_values:
            place_market_order(info['symbol'], info['order_type'], float(format(float(volume_per_tp), '.2f')), float(info['sl']), float(tp))
            print(f"Placed order for {float(format(float(volume_per_tp), '.2f'))} lots of {info['symbol']} at {info['order_type']} {info['order_price']} with SL {info['sl']} and TP {tp}")
            msg.append(f"TP {i}: Placed order for {float(format(float(volume_per_tp), '.2f'))} lots of {info['symbol']} at {info['order_type']} {info['order_price']} with SL {info['sl']} and TP {tp}")
            i += 1

        context.bot.send_message(my_user_id, "\n".join(msg))

def extract_order_info(text: str) -> dict:
    results = {}
    symbol_match = re.search(r'\b\w{6}\b', text)
    if symbol_match:
        results['symbol'] = symbol_match.group(0)

    order_type_match = re.search(r'(BUY|SELL)', text, re.IGNORECASE)
    if order_type_match:
        results['order_type'] = order_type_match.group(1).upper()

    price_match = re.search(
        r'(BUY|SELL)(?:\s+NOW)?\s+([\d\.]+)(?:\/[\d\.]+)?|Entry\s*:\s*([\d\.]+)', text, re.IGNORECASE
    )

    if price_match:
        # Check if the first group (BUY/SELL price) matched or the third group (Entry price)
        if price_match.group(2):
            results['order_price'] = float(format(float(price_match.group(2)), ".3f"))
        elif price_match.group(3):
            results['order_price'] = float(format(float(price_match.group(3)), ".3f"))

    sl_match = re.search(r'SL\s*:?\s*([\d:,\']+)(?=\D|$)', text, re.IGNORECASE)
    if sl_match:
        sl_value = sl_match.group(1).replace(",", "").replace("'", ".").replace(":", ".")
        results['sl'] = float(format(float(sl_value), ".3f"))

    tpReplacePattern = r'(Tp\d*\s*);'
    def replace_semicolon(match):
        return match.group(0).replace(';', ':')

    updated_text = re.sub(tpReplacePattern, replace_semicolon, text, flags=re.IGNORECASE)
    tp_matches = re.findall(r'TP\w?\s*:?\s*([\d:,\']+)(?=\D|$)', updated_text, re.IGNORECASE)
    for index, tp_value in enumerate(tp_matches, start=1):
        tp_value = tp_value.replace(",", "").replace("'", ".").replace(":", ".")
        key = f"tp{index}"
        results[key] = float(format(float(tp_value), ".3f"))

    return results

def place_market_order(symbol, action, volume, sl, tp):
    if action == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        tick_info = mt5.symbol_info_tick(symbol)
        if tick_info is None:
            print(f"Could not fetch tick data for symbol: {symbol}")
            return
        price = tick_info.ask
    elif action == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
        tick_info = mt5.symbol_info_tick(symbol)
        if tick_info is None:
            print(f"Could not fetch tick data for symbol: {symbol}")
            return
        price = tick_info.bid
    else:
        print(f"Unknown action: {action}")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 99999,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

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

def run_bot():
    updater = Updater(token, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    initialize_bot()
    run_bot()
