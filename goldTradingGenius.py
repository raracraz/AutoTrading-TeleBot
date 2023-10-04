import configparser
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater
import logging
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read the token and your user ID from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

my_username = config.get('Telegram', 'my_username')
my_user_id = int(config.get('Telegram', 'my_user_id'))  # Add your_user_id to your config file

token = config.get('TradingBot', 'token')

def handle_message(update: Update, context: CallbackContext) -> None:
    print(f"Received update: {update}")
    # Check if the update contains a message object
    if not update.message:
        print("Received an update without a message")
        return

    # Print the received message to the terminal
    print(f"Received message: {update.message.text}")
    
    context.bot.send_message(my_user_id, f"Received a new message")
    
    # Extract the text from the message
    text = update.message.text
    
    if text.startswith("🔷XAUUSD GOLD"):
        print(f"Received matching message: {text}")
        context.bot.send_message(my_user_id, f"Received a new matching message: {text}")


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
