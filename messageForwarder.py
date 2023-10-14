import configparser
import logging
from telethon import TelegramClient, events
import re

# logging.basicConfig(level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('Telegram', 'api_id')
api_hash = config.get('Telegram', 'api_hash')
phone_number = config.get('Telegram', 'phone_number')
source_channel_id = int(config.get('Telegram', 'source_channel_id'))
dest_channel_username = config.get('Telegram', 'dest_channel_username')
dest_channel_id = int(config.getint('Telegram', 'dest_channel_id'))  # Assuming it's an integer ID like the source
my_username = config.get('Telegram', 'my_username')

client = TelegramClient('default_session', api_id, api_hash)

async def main():
    await client.start(phone_number)

    print('Client Created...')
    print('Connecting to Telegram Servers...')
    print('Done, now forwarding messages...')

    try:
        # Send a start message to the destination channel when the bot starts
        await client.send_message(dest_channel_username, f'Bot has started! And is forwarding messages from ID: {source_channel_id} to: {dest_channel_username}')
    except Exception as e:
        print(f"Error occurred when sending start message: {e}")
    
    @client.on(events.NewMessage(chats=source_channel_id))
    async def handler(event):
        # Check if the message starts with the desired patterns
        message_text = event.message.text
        if message_text:
            if re.search(r'\s?([A-Z]{6})\s', message_text):
                print(event.message)  # Print the incoming message to the console
                try:
                    # Forward the incoming message to the destination channel
                    await client.forward_messages(dest_channel_id, event.message)
                    
                except Exception as e:
                    print(f"Error occurred: {e}")

    
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())