import telegram
import configparser
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater
import logging
import time
import re
import os
import MetaTrader5 as mt5
import math

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        if re.search(r'close half lots', text, re.IGNORECASE):
            print(f"Received close half lots message: {text}")
            context.bot.send_message(my_user_id, f"Received a close half lots message: \n\n{text}")
            
            # Extract the new SL value
            sl_match = re.search(r'MOVE SL to ([\d.]+)', text)
            if sl_match:
                new_sl = float(sl_match.group(1))
                symbol = extract_symbol(text)
                if symbol:
                    close_half_and_update_sl(symbol, new_sl)
                    context.bot.send_message(my_user_id, f"Closed half position and updated SL for {symbol} to {new_sl}")
                    return
                else:
                    print("Could not extract symbol from the message")
            else:
                print("Could not extract new SL value from the message")
        
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

def extract_symbol(text: str) -> str:
    symbol_match = re.search(r'\b([A-Z]{6})\b', text)
    return symbol_match.group(1) if symbol_match else None

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
        "comment": "python script op",
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

def close_half_and_update_sl(symbol: str, new_sl: float):
    positions = mt5.positions_get(symbol=symbol)
    
    if positions:
        for position in positions:
            # Check if this position has already been partially closed
            if "python script cl" not in position.comment:
                half_volume = math.floor(position.volume * 50) / 100  # Round down to 2 decimal places
                
                if half_volume > 0:
                    # Close half of this position
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": half_volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,
                        "price": mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask,
                        "deviation": 20,
                        "magic": 100,
                        "comment": "python script cl",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    
                    close_result = mt5.order_send(close_request)
                    if close_result.retcode != mt5.TRADE_RETCODE_DONE:
                        print(f"Failed to close half of position {position.ticket}. Error: {close_result.comment}")
                    else:
                        print(f"Successfully closed {half_volume} lots of position {position.ticket} for {symbol}")
                    
                    # Update the comment for the remaining position to indicate it has been partially closed
                    modify_comment_request = {
                        "action": mt5.TRADE_ACTION_MODIFY,
                        "position": position.ticket,
                        "comment": "python script close half"
                    }
                    modify_comment_result = mt5.order_send(modify_comment_request)
                    if modify_comment_result.retcode != mt5.TRADE_RETCODE_DONE:
                        print(f"Failed to update comment for position {position.ticket}. Error: {modify_comment_result.comment}")
                    else:
                        print(f"Successfully updated comment for position {position.ticket}")
            else:
                print(f"Position {position.ticket} has already been partially closed. Skipping.")
            
            # Update stop loss for all positions, regardless of whether they were just closed or not
            modify_request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "symbol": symbol,
                "sl": new_sl,
                "tp": position.tp
            }
            
            modify_result = mt5.order_send(modify_request)
            if modify_result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to update stop loss for position {position.ticket}. Error: {modify_result.comment}")
            else:
                print(f"Successfully updated stop loss for position {position.ticket} to {new_sl}")
        
        print(f"Finished closing half of eligible positions and updating stop losses for {symbol}")
    else:
        print(f"No open positions found for {symbol}")

def run_bot():
    retry_attempts = 0
    max_retries = 5
    backoff_time = 10  # Initial backoff time
    cooldown_time = 300  # 5 minutes cooldown after max retries

    while True:
        try:
            # Create Updater object and pass in the bot's token.
            updater = Updater(token, use_context=True)
    
            dp = updater.dispatcher
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

            # Start the bot
            updater.start_polling()
            updater.idle()

        except telegram.error.NetworkError as e:
            logging.error(f"Network error encountered: {e}. Retrying in {backoff_time} seconds...")
            retry_attempts += 1
            updater.stop()  # Stop the updater to force it to restart

            if retry_attempts > max_retries:
                logging.error(f"Max retry attempts reached. Pausing for {cooldown_time // 60} minutes.")
                time.sleep(cooldown_time)  # Pause for 5 minutes
                retry_attempts = 0  # Reset retry attempts after cooldown

            time.sleep(backoff_time)
            continue  # Retry after waiting
        except Exception as e:
            logging.error(f"Unexpected error: {e}. Retrying in 10 seconds...")
            updater.stop()  # Stop the updater on any other error as well
            time.sleep(10)
            continue

if __name__ == '__main__':
    initialize_bot()
    run_bot()
