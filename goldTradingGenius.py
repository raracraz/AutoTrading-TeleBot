import configparser
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters, Updater
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read the token and your user ID from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

my_username = config.get('Telegram', 'my_username')
my_user_id = int(config.get('Telegram', 'my_user_id'))  # Add your_user_id to your config file

token = config.get('TradingBot', 'token')

def handle_message(update: Update, context: CallbackContext) -> None:

    context.bot.send_message(my_user_id, f"Received a new message")
    
    # Extract the text from the message
    if update.message:
        text = update.message.text
    else:
        # Handle other types of updates or simply return
        return
    
    # Check if the message starts with "🔷XAUUSD GOLD"
    if text.startswith("🔷XAUUSD GOLD"):

        print(f"Received matching message: {text}")
        
        # Send a Telegram notification to yourself
        context.bot.send_message(my_user_id, f"Received a new matching message: {text}")
        
        print(f"Received message: {text}")
        # Additional processing logic can be added here if needed

# Create an updater and pass your bot's token
updater = Updater(token=token)

# On each message, call the 'handle_message' function
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
try:
    updater.start_polling()
    print("Bot started polling...")
except Exception as e:
    print(f"Error occurred while starting the bot: {e}")
    exit(1)
updater.idle()
