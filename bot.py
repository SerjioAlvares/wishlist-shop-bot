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


START, SELECTING_LANGUAGE, SELECTING_ACTION = range(1, 4)


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
        SELECTING_LANGUAGE: handle_language_selection,
        SELECTING_ACTION: handle_action_selection
    }
    user_state = (
        START
        if user_reply == '/start'
        else context.user_data['next_state'] or START
    )
    state_handler = states_functions[int(user_state)]
    next_state = await state_handler(update, context)
    context.user_data['next_state'] = next_state


async def handle_start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the START state."""
    text = 'Выбери, пожалуйста, язык / Please, select language'
    buttons = [[
        InlineKeyboardButton('🇷🇺 Русский', callback_data='russian'),
        InlineKeyboardButton('🇬🇧 English', callback_data='english')
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard)
    return SELECTING_LANGUAGE


async def handle_language_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the SELECTING_LANGUAGE state."""
    query = update.callback_query
    if not query:
        next_state = await handle_start_command(update, context)
        return next_state

    await update.callback_query.answer()
    # await context.bot.delete_message(
    #     chat_id=update.effective_chat.id,
    #     message_id=query.message.message_id
    # )

    text = ''
    if query.data == 'english':
        text = "Sorry, the English selection doesn't work yet./n/n"

    text = f'{text}Выбери, пожалуйста, что ты хочешь сделать'
    buttons = [
        [
            InlineKeyboardButton(
                'Выбрать впечатление',
                callback_data='impression'
            ),
            InlineKeyboardButton(
                'Активировать сертификат',
                callback_data='certificate'
            )
        ],
        [
            InlineKeyboardButton('F.A.Q. и поддержка', callback_data='faq')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # await update.message.reply_text(text=text, reply_markup=keyboard)
    return SELECTING_ACTION


async def handle_action_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the SELECTING_ACTION state."""
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
    application.add_handler(MessageHandler(filters.TEXT, handle_users_reply))
    application.add_handler(CommandHandler('start', handle_users_reply))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
