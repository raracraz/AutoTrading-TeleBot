import configparser
from telethon import TelegramClient, events

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('Telegram', 'api_id')
api_hash = config.get('Telegram', 'api_hash')
phone_number = config.get('Telegram', 'phone_number')
source_channel_username = config.get('Telegram', 'source_channel_username')
dest_channel_username = config.get('Telegram', 'dest_channel_username')
source_channel_id = config.get('Telegram', 'source_channel_id')
dest_channel_id = config.get('Telegram', 'dest_channel_id')

client = TelegramClient('default_session', api_id, api_hash)

async def main():
    await client.start(phone_number)

    try:
        # Send a message to the destination channel when the bot starts
        await client.send_message(dest_channel_username, 'Bot has started! And is forwarding messages from: ' + source_channel_username + ' to: ' + dest_channel_username + '')
    except Exception as e:
        print(f"Error occurred when sending start message: {e}")
    
    @client.on(events.NewMessage(chats=source_channel_id))
    async def handler(event):
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
