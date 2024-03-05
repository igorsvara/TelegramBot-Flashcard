from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json

TOKEN: Final = ""
BOT_USERNAME: Final = ""

# Apri il file JSON con le domande/risposte
with open('topics/Torrent/core_torrent.json', 'r', encoding='utf-8') as file:
    domande_risposte = json.load(file)


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there! Let us begin.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let me help. Please type something so I can respond.")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Button 1", callback_data='button1')],
        [InlineKeyboardButton("Button 2", callback_data='button2')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Custom command in action! Choose an option:", reply_markup=reply_markup)



# Bot Response
def handle_response(text: str):
    processed: str = text.lower()

    if "hello" in processed:
        return "Hi there!"

    if "how are you" in processed:
        return "Feeling great, what about you?"

    if "tell me something" in processed:
        return "You are amazing the way you are."

    return "Sorry, I don't understand..."


# Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print(f'Bot: {response}')
    await update.message.reply_text(response)


# Button
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Handle the response to the button click
    chosen_option = query.data
    await query.edit_message_text(text=f"You chose: {chosen_option}")


# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error {context.error}')


if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)  # 3 seconds