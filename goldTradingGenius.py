from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace YOUR_BOT_TOKEN with the token you received from the BotFather
updater = Updater("YOUR_BOT_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot has started!')

def forward(update: Update, context: CallbackContext) -> None:
    # Replace DESTINATION_CHAT_ID with the ID of the chat you want to forward messages to
    context.bot.send_message(chat_id=DESTINATION_CHAT_ID, text=update.message.text)

def main():
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    # Replace SOURCE_CHAT_ID with the ID of the chat you want to read messages from
    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHAT_ID) & Filters.text & ~Filters.command, forward))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
