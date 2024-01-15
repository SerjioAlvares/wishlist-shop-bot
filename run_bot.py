# coding=utf-8
"""Organize the work of the impressions telegram bot."""
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
    MessageHandler
)


START, SELECTING_LANGUAGE, SELECTING_ACTION, SELECTING_IMPRESSION = range(1, 5)


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
        SELECTING_LANGUAGE: handle_language_menu,
        SELECTING_ACTION: handle_action_menu
    }
    chat_state = (
        START
        if user_reply == '/start'
        else context.chat_data.get('next_state') or START
    )
    state_handler = states_functions[int(chat_state)]
    next_state = await state_handler(update, context)
    context.chat_data['next_state'] = next_state


async def handle_start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the start command."""
    text = 'Выбери, пожалуйста, язык / Please, select language'
    keyboard = [[
        InlineKeyboardButton('🇷🇺 Русский', callback_data='russian'),
        InlineKeyboardButton('🇬🇧 English', callback_data='english')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return SELECTING_LANGUAGE


async def send_action_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str
) -> int:
    """Send the Action selection menu to chat."""
    text = f'{text}Выбери, пожалуйста, что ты хочешь сделать'
    keyboard = [
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )
    return SELECTING_ACTION


async def handle_language_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the Language selection menu."""
    query = update.callback_query
    if not query:
        next_state = await handle_start_command(update, context)
        return next_state

    await update.callback_query.answer()

    text = ''
    if query.data == 'english':
        text = "Sorry, the English selection doesn't work yet.\n\n"
        await update.callback_query.answer(text=text)

    next_state = await send_action_menu(update, context, text)
    return next_state


async def handle_action_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the Action selection menu."""
    query = update.callback_query
    if not query:
        next_state = await handle_start_command(update, context)
        return next_state

    await update.callback_query.answer()

    if query.data == 'impression':
        next_state = await handle_impression_button(update, context)
        return next_state

    if query.data == 'certificate':
        next_state = await handle_certificate_button(update, context)
        return next_state

    if query.data == 'faq':
        next_state = await handle_faq_button(update, context)
        return next_state


async def handle_impression_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the Impression button click."""
    impressions = await Database.get_impressions()
    if not impressions:
        text = 'Извини впечатлений пока нет.\n'
        next_state = await send_action_menu(update, context, text)
        return next_state

    text = 'Выбери впечатление:\n\n'
    keyboard = []
    for impression_index, impression in enumerate(impressions):
        text += (
            f"*{impression['id']}\.* "  # noqa: W605
            f"[{impression['name']} "
            f"\- цена {impression['price']}]"  # noqa: W605
            f"({impression['url']})\n"
        )
        if not (impression_index % 5):
            keyboard.append([])
        keyboard[-1].append(InlineKeyboardButton(
            f"{impression['id']}",
            callback_data=f"impression_{impression['id']}")
        )

    text += '\n'
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text,
        parse_mode='MarkdownV2',
        # disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    return SELECTING_IMPRESSION


async def handle_certificate_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the Certificate button click."""
    text = "Извини, эта кнопка пока не работает.\n\n"
    next_state = await send_action_menu(update, context, text)
    return next_state


async def handle_faq_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the FAQ button click."""
    text = "Извини, эта кнопка пока не работает.\n\n"
    next_state = await send_action_menu(update, context, text)
    return next_state


def main() -> None:
    """Run the bot."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    persistence = DjangoPersistence()

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
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'impressions.settings')
    django.setup()

    from bot.persistence import DjangoPersistence
    from bot.database import Database
    main()
