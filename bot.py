from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, \
    ConversationHandler
import json

from mytoken import TOKEN, BOT_USERNAME

CHOSE_DECK, CHOSE_CARD, SHOW_CARD, SHOW_ANSWER = range(4)

# Apri il file JSON con le domande/risposte
with open('topics/Torrent/core_torrent.json', 'r', encoding='utf-8') as file:
    domande_risposte = json.load(file)

deck_list = ["SO", "CPS", "ASD", "DB"]

l = [f"{i} -> {answer['testo']}" for i, answer in enumerate(domande_risposte[0]["opzioni"])]
print(l)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there! Let us begin.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let me help. Please type something so I can respond.")


# Messages
def handle_response(text: str):
    processed: str = text.lower()

    if processed in ["hello", "hi", "good morning"]:
        return "Hi there!"

    return "I'm not jet trained to understand that, sorry."


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


# Conversation
async def flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("decks", callback_data="decks"),
                InlineKeyboardButton("exit", callback_data="exit")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("FLASHCARDS GAME, this bot helps you study.", reply_markup=reply_markup)

    return CHOSE_DECK


async def chose_decks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    col_per_row = 2

    keyboard = [[InlineKeyboardButton(f"{deck}", callback_data=f"deck{i}")
                for i, deck in enumerate(deck_list[x:x+col_per_row])] for x in range(0, len(deck_list), col_per_row)]

    keyboard.append([InlineKeyboardButton("EXIT", callback_data="exit")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "This are the available decks.\n"
        "Chose one:",
        reply_markup=reply_markup
    )

    return CHOSE_CARD


# TODO: trova il momento in cui vanno eliminati i dati dell'utente
async def chose_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query
    await query.answer()

    if query.data in ['good', 'mid', 'bad']:
        deck_chosen = user_data["deck_selected"]
    else:
        deck_chosen = int(query.data[4:])
        user_data["deck_selected"] = deck_chosen

    # TODO: fai refactor di callback "domanda" con "card"
    keyboard = [[InlineKeyboardButton(f"{card['domanda']}", callback_data=f"domanda{i}")]
                for i, card in enumerate(domande_risposte)]
    keyboard.append([InlineKeyboardButton("EXIT", callback_data="exit")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # TODO: deck_chosen = deck0/1/2... not the name itself
    await query.edit_message_text(f"Deck {deck_chosen} has the following cards:", reply_markup=reply_markup)

    return SHOW_CARD


async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query
    await query.answer()

    # TODO: valuta di usare regex invece dello slicing per estrarre il numero
    card_chosen = int(query.data[7:])
    user_data["card_selected"] = card_chosen

    keyboard = [[InlineKeyboardButton(f"{answer['testo']}", callback_data=f"option{i}")]
                for i, answer in enumerate(domande_risposte[card_chosen]['opzioni'])]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"{domande_risposte[card_chosen]['domanda']}\n"
        "Chose one:",
        reply_markup=reply_markup)

    return SHOW_ANSWER


async def rate_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query
    await query.answer()

    deck_chosen = user_data["deck_selected"]
    card_chosen = user_data["card_selected"]
    ans_chosen = int(query.data[6:])

    keyboard = [[InlineKeyboardButton(f"GOOD", callback_data="good"),
                 InlineKeyboardButton(f"MID", callback_data="mid"),
                 InlineKeyboardButton(f"BAD", callback_data="bad")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    card = domande_risposte[card_chosen]
    risposta_usr = card['opzioni'][ans_chosen]['testo']
    risposta_corretta = ""
    for opzione in card['opzioni']:
        if opzione['corretta']:
            risposta_corretta = opzione['testo']

    testo = f"Alla domanda: {card['domanda']}\n"
    if risposta_usr == risposta_corretta:
        testo += "Hai risposto correttamente!\n"
        testo += risposta_corretta
    else:
        testo += "Sbagliato, la risposta corretta e':"
        testo += risposta_corretta

    await query.edit_message_text(
        testo,
        reply_markup=reply_markup)

    del user_data["card_selected"]
    return CHOSE_CARD


# User data
async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: implementa un dizionario all'interno dei dati dell'utente in cui memorizzo tutte le domande svolte con il tempo rimanente per la notifica
    #   se la domanda nel frattempo viene risolta nuovamente il time viene sovrascritto
    # data = ""
    # await update.message.reply_text("This is the data I have:\n")
    return


async def delete_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


# Exit
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query
    await query.answer()

    user_data.clear()
    await query.edit_message_text("La sessione e' finita, alla prossima!")
    return ConversationHandler.END


# Errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'ERROR: Update {update.update_id} caused an error {context.error}')
    # await update.message.reply_text("There was an error.")


if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('show_data', show_data))
    app.add_handler(CommandHandler('delete_data', delete_data))

    deck_conversation = ConversationHandler(
        entry_points=[CommandHandler('flashcard', flashcard)],
        states={
            CHOSE_DECK: [
                CallbackQueryHandler(chose_decks, pattern="^decks$"),
                CallbackQueryHandler(cancel, pattern="^exit$")
            ],
            CHOSE_CARD: [
                CallbackQueryHandler(chose_cards, pattern="^deck"),
                CallbackQueryHandler(chose_cards, pattern="^(good|mid|bad)"),
                CallbackQueryHandler(cancel, pattern="^exit$")
            ],
            SHOW_CARD: [
                CallbackQueryHandler(show_options, pattern="^domanda"),
                CallbackQueryHandler(chose_decks, pattern="^back$"),
                CallbackQueryHandler(cancel, pattern="^exit$")
            ],
            SHOW_ANSWER: [
                CallbackQueryHandler(rate_answer, pattern="^option")
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(deck_conversation)
    # TODO: find a way to practise with this questions
    app.add_handler(CommandHandler('train_deck', flashcard))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)  # 3 seconds