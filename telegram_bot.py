# coding=utf-8
"""Organize the work of the selling certificates telegram bot."""
import os
from contextlib import suppress

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
)


START = range(1, 2)


def run_telegram_bot(tg_bot_token):
    """Launch a telegram bot and organize its work."""

    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()


def handle_users_reply(update, context):
    """Handle all user actions."""
    handle_start_command(update, context)


def handle_start_command(update, context):
    """Handle the START state."""
    query = update.callback_query
    if not query:
        with suppress(BadRequest):
            context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id-1
            )

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton('Ru', callback_data='Ru'),
        InlineKeyboardButton('Eng', callback_data='Eng')
    ]])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выбери, пожалуйста, язык / Please, select language',
        reply_markup=keyboard
    )


def main():
    load_dotenv()
    tg_bot_token = os.environ['TELEGRAM_BOT_TOKEN']

    run_telegram_bot(tg_bot_token)


if __name__ == '__main__':
    main()
