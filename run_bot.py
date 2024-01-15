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


START, SELECTING_LANGUAGE, MAIN_MENU, SELECTING_IMPRESSION, SELECTING_DELIVERY = range(1, 6)


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
        MAIN_MENU: handle_main_menu,
        SELECTING_IMPRESSION: handle_impressions_menu,
        SELECTING_DELIVERY: handle_deliveries_menu,
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


async def handle_language_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Language selecting menu."""
    query = update.callback_query
    if not query:
        next_state = await handle_start_command(update, context)
        return next_state

    await update.callback_query.answer()
    context.chat_data['language'] = update.callback_query.data

    text = ''
    if update.callback_query.data == 'english':
        text = "Sorry, the English selection doesn't work yet.\n\n"
        await update.callback_query.answer(text=text)

    next_state = await send_main_menu(update, context, text)
    return next_state


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Send Main menu to chat."""
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
    return MAIN_MENU


async def handle_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Main menu."""
    query = update.callback_query
    if not query:
        text = 'Извини, выбор непонятен. Попробуй ещё раз.\n\n'
        next_state = await send_main_menu(update, context, text)
        return next_state

    await update.callback_query.answer()

    if query.data == 'impression':
        next_state = await send_impressions_menu(update, context)
        return next_state

    if query.data == 'certificate':
        next_state = await handle_certificate_button(update, context)
        return next_state

    if query.data == 'faq':
        next_state = await handle_faq_button(update, context)
        return next_state


def calculate_buttons_in_row(buttons_count: int) -> int:
    """Count how many buttons to place in a row."""
    buttons_in_row = 5
    if buttons_count <= buttons_in_row:
        return buttons_count

    if not buttons_count % buttons_in_row:
        if buttons_count % buttons_in_row > 1:
            return buttons_in_row

        for buttons_in_row in range(7, 3, -1):
            if buttons_count % buttons_in_row > 1:
                return buttons_in_row
    return 5


async def send_impressions_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Handle Impression button click."""
    impressions = await Database.get_impressions()
    if not impressions:
        text = 'Извини, впечатлений пока нет.\n'
        next_state = await send_main_menu(update, context, text)
        return next_state

    text = f'{text}Выбери впечатление:\n\n'
    keyboard = []
    buttons_in_row = calculate_buttons_in_row(buttons_count=len(impressions))
    for impression_index, impression in enumerate(impressions):
        impression_title = (
            f"{impression['id']}\. "  # noqa: W605
            f"{impression['name']} "
            f"\- {impression['price']} ₽"  # noqa: W605
        )
        text += f"[{impression_title}]({impression['url']})\n"
        if not (impression_index % buttons_in_row):
            keyboard.append([])
        keyboard[-1].append(InlineKeyboardButton(
            f"{impression['id']}",
            callback_data=impression_title)
        )

    keyboard.append([
        InlineKeyboardButton(
            '« Вернуться в главное меню',
            callback_data='main_menu'
        )
    ])

    text += '\n'
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return SELECTING_IMPRESSION


async def handle_impressions_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Impression selecting."""
    query = update.callback_query
    if not query:
        next_state = handle_unrecognized_impression(update, context)
        return next_state

    await update.callback_query.answer()

    if update.callback_query.data == 'main_menu':
        next_state = await send_main_menu(update, context)
        return next_state

    point_index = update.callback_query.data.find('\.')  # noqa: W605
    if point_index == -1:
        next_state = handle_unrecognized_impression(update, context)
        return next_state

    impression_number = update.callback_query.data[:point_index]
    print(impression_number)
    if not impression_number.isnumeric():
        next_state = await handle_unrecognized_impression(update, context)
        return next_state

    context.chat_data['impression'] = update.callback_query.data
    next_state = await send_deliveries_menu(update, context)
    return next_state


async def handle_unrecognized_impression(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle unrecognized_impression."""
    text = (
        'Извини, непонятно, какое впечатление ты хочешь '  # noqa: W605
        'выбрать\. Попробуй выбрать ещё раз\.\n\n'  # noqa: W605
    )
    next_state = await send_impressions_menu(update, context, text)
    return next_state


async def send_deliveries_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Send Deliveries menu to chat."""
    text = (
        f'{text}Отличный выбор: Ты выбрал(а) сертификат:\n*' +
        context.chat_data['impression'] +
        '*\n\nВ какой форме хочешь получить его?'
    )
    keyboard = [
        [
            InlineKeyboardButton(
                '📧 По электронной почте',
                callback_data='email'
            ),
            InlineKeyboardButton(
                '📨 В подарочной коробке',
                callback_data='gift_box'
            ),
        ],
        [
            InlineKeyboardButton(
                '‹ Выбрать другое впечатление',
                callback_data='impression'
            )
        ],
        [
            InlineKeyboardButton(
                '« Вернуться в главное меню',
                callback_data='main_menu'
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return SELECTING_DELIVERY


async def handle_deliveries_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Delivery selecting."""
    query = update.callback_query
    if not query:
        text = (
            'Извини, непонятно, какой способ получения сертификата ты хочешь '
            'выбрать\. Попробуй выбрать ещё раз\.\n\n'  # noqa: W605
        )
        next_state = await send_deliveries_menu(update, context, text)
        return next_state

    await update.callback_query.answer()

    if update.callback_query.data == 'impression':
        next_state = await send_impressions_menu(update, context)
        return next_state

    if update.callback_query.data == 'email':
        next_state = await handle_email_button(update, context)
        return next_state

    if update.callback_query.data == 'gift_box':
        next_state = await handle_gift_box_button(update, context)
        return next_state


async def handle_email_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Email button click."""
    text = 'Напиши почту, на которую хотел(а) бы получить сертификат:'
    next_state = await send_main_menu(update, context, text)
    return next_state


async def handle_gift_box_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Gift-box button click."""
    text = "Извини, эта кнопка пока не работает.\n\n"
    next_state = await send_main_menu(update, context, text)
    return next_state


async def handle_certificate_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Certificate button click."""
    text = "Извини, эта кнопка пока не работает.\n\n"
    next_state = await send_main_menu(update, context, text)
    return next_state


async def handle_faq_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the FAQ button click."""
    text = "Извини, эта кнопка пока не работает.\n\n"
    next_state = await send_main_menu(update, context, text)
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
