# Autotrading Bot
AutoTrading Bot is an automated trading system that interfaces with MetaTrader 5 (MT5) to execute trades based on signals received via Telegram.
```
[SYMBOL] [BUY/SELL] [OPEN PRICE]
TP [TP 1 Value]
TP [TP 2 Value]
TP [TP 3 Value]
TP [TP 4 Value]
...

SL [SL Value]
```

## Features
- Automatically places trades in MT5 based on Telegram signals.
- Supports multiple Take Profit (TP) levels.
- Graceful error handling and logging capabilities.
- Automatic retries on network issues.
- Best used when ran on a cloud server so that it provides 24/7 coverage.

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

## Architecture Diagram
![Tele Trading Bot](https://github.com/raracraz/AutoTrading-TeleBot/assets/88528326/c4f4afc3-f7ba-4f9c-9142-f48b1c746dee)

## Issues
- The script can currently only handle one lot size value.
