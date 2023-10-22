# Autotrading Bot
AutoTrading Bot is an automated trading system that interfaces with MetaTrader 5 (MT5) to execute trades based on signals received via Telegram.

## Features
- Automatically places trades in MT5 based on Telegram signals.
- Supports multiple Take Profit (TP) levels.
- Graceful error handling and logging capabilities.
- Automatic retries on network issues.

## Prerequisites
- Python 3.11 or higher.
- MetaTrader 5 terminal with a trading account.
- Access to a Telegram channel or group that sends trading signals.
- Create a config.ini file in the same directory as the script with the following contents:

```
[Telegram]
api_id = YOUR_TELEGRAM_API_ID
api_hash = YOUR_TELEGRAM_API_HASH
phone_number = YOUR_TELEGRAM_PHONE_NUMBER
source_channel_id = SOURCE_CHANNEL_ID
dest_channel_username = DEST_CHANNEL_USERNAME
dest_channel_id = DEST_CHANNEL_ID
my_username = YOUR_TELEGRAM_USERNAME
my_user_id = YOUR_USER_ID

[TradingBot]
token = YOUR_BOT_TOKEN

[MetaTrader]
login = YOUR_MT5_LOGIN
password = YOUR_MT5_PASSWORD
server = YOUR_MT5_SERVER

[Settings]
lot_size = DESIRED_LOT_SIZE
```

## Issues
- The script can currently only handle one lot size value.