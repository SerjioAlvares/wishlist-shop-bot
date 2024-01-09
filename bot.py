# coding=utf-8
"""Organize the work of the selling certificates telegram bot."""
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    filters,
    MessageHandler,
    PicklePersistence
)


START, SELECTING_LANGUAGE = [str(i) for i in range(1, 3)]


async def handle_users_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle all user actions."""
    if not update.message and not update.callback_query:
        return

    user_reply = (
        update.message.text
        if update.message
        else update.callback_query.data
    )

    states_functions = {
        START: handle_start_command,
        SELECTING_LANGUAGE: handle_language_selection
    }
    user_state = (
        START
        if user_reply == '/start'
        else context.user_data['next_state'] or START
    )
    state_handler = states_functions[user_state]

    next_state = await state_handler(update, context)
    context.user_data['next_state'] = next_state


async def handle_start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Handle the START state."""
    text = 'Выбери, пожалуйста, язык / Please, select language'
    keyboard = [[
        InlineKeyboardButton('🇷🇺 Русский', callback_data='Russian'),
        InlineKeyboardButton('🇬🇧 English', callback_data='English')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return SELECTING_LANGUAGE


async def handle_language_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Handle the SELECTING_LANGUAGE state."""
    pass


def main() -> None:
    """Run the bot."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    persistence = PicklePersistence(
        filepath='bot-states.pckl',
        update_interval=1
    )
    application = (
        Application.builder()
        .token(bot_token)
        .read_timeout(50)
        .write_timeout(50)
        .get_updates_read_timeout(50)
        .persistence(persistence)
        .build()
    )

    application.add_handler(CallbackQueryHandler(handle_users_reply))
    application.add_handler(MessageHandler(filters.Text, handle_users_reply))
    application.add_handler(CommandHandler('start', handle_users_reply))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
