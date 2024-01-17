# coding=utf-8
"""Organize the work of the impressions telegram bot."""
import logging
import os
import re

import phonenumbers
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
from telegram.helpers import escape_markdown


(START, SELECTING_LANGUAGE, MAIN_MENU, SELECTING_IMPRESSION,
 SELECTING_RECEIVING_METHOD, WAITING_EMAIL, ACQUAINTED_PRIVACY_POLICY,
 WAITING_FULLNAME, WAITING_PHONE_NUMBER,
 WAITING_PAYMENT_SCREENSHOT, DIALOGUE_END) = range(1, 12)


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
        SELECTING_RECEIVING_METHOD: handle_receiving_methods_menu,
        WAITING_EMAIL: handle_email_message,
        ACQUAINTED_PRIVACY_POLICY: handle_privacy_policy_button,
        WAITING_FULLNAME: handle_fullname_message,
        WAITING_PHONE_NUMBER: handle_phone_number_message,
        WAITING_PAYMENT_SCREENSHOT: handle_payment_screenshot,
        DIALOGUE_END: handle_dialogue_end
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

    next_state = await send_main_menu(update, context)
    return next_state


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Send Main menu to chat."""
    if context.chat_data['language'] == 'russian':
        message = 'Выбери, пожалуйста, что ты хочешь сделать'
        buttons = [
            'Выбрать впечатление',
            'Активировать сертификат',
            'F.A.Q. и поддержка'
        ]
    else:
        message = 'Please choose what you want to do'
        buttons = [
            'Select an impression',
            'Activate certificate',
            'F.A.Q. and support'
        ]

    text = f'{text}{message}'
    keyboard = [
        [
            InlineKeyboardButton(buttons[0], callback_data='impression'),
            InlineKeyboardButton(buttons[1], callback_data='certificate')
        ],
        [
            InlineKeyboardButton(buttons[2], callback_data='faq')
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
        if context.chat_data['language'] == 'russian':
            text = (
                'Извини, непонятно, что ты хочешь выбрать. '
                'Попробуй ещё раз.\n\n'
            )
        else:
            text = (
                "Sorry, it's not clear what you want to choose. "
                "Try again.\n\n"
            )
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
    """Send Impressions menu."""
    impressions = await Database.get_impressions(context.chat_data['language'])
    if not impressions:
        if context.chat_data['language'] == 'russian':
            text = 'Извини, впечатлений пока нет.\n'
        else:
            text = 'Sorry, no impressions yet.\n'
        next_state = await send_main_menu(update, context, text)
        return next_state

    if context.chat_data['language'] == 'russian':
        text = f'{normalise_text(text)}Выбери впечатление:\n\n'
        button = '« Вернуться в главное меню'
    else:
        text = f'{normalise_text(text)}Choose an impression:\n\n'
        button = '« Back to main menu'

    keyboard = []
    buttons_in_row = calculate_buttons_in_row(buttons_count=len(impressions))
    for impression_index, impression in enumerate(impressions):
        impression_title = normalise_text(
            f"{impression['id']}. "
            f"{impression['name']} "
            f"- {impression['price']}"
        )
        text += f"[{impression_title}]({impression['url']})\n"
        if not (impression_index % buttons_in_row):
            keyboard.append([])
        keyboard[-1].append(InlineKeyboardButton(
            f"{impression['id']}",
            callback_data=impression_title)
        )

    keyboard.append([InlineKeyboardButton(button, callback_data='main_menu')])

    text += '\n'
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return SELECTING_IMPRESSION


def normalise_text(text: str) -> str:
    """Normalise text for parsing in Telegram."""
    escape_chars = r'_[]()~`>#+-=|{}.!'
    new_text = ''
    old_character = ''
    for character in text:
        if character in escape_chars and old_character != '\\':
            new_text += '\\'
        new_text += character
        old_character = character
    return new_text


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

    point_index = update.callback_query.data.find(normalise_text('.'))
    if point_index == -1:
        next_state = handle_unrecognized_impression(update, context)
        return next_state

    impression_number = update.callback_query.data[:point_index]
    print(impression_number)
    if not impression_number.isnumeric():
        next_state = await handle_unrecognized_impression(update, context)
        return next_state

    context.chat_data['impression'] = update.callback_query.data
    next_state = await send_receiving_methods_menu(update, context)
    return next_state


async def handle_unrecognized_impression(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle unrecognized_impression."""
    if context.chat_data['language'] == 'russian':
        text = (
            'Извини, непонятно, какое впечатление ты хочешь '
            'выбрать. Попробуй выбрать ещё раз.\n\n'
        )
    else:
        text = (
            "Sorry, it's not clear which experience you want to "
            "choose. Try choosing again.\n\n"
        )

    next_state = await send_impressions_menu(update, context, text)
    return next_state


async def send_receiving_methods_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Send to chat Menu of ways to receive order."""
    if context.chat_data['language'] == 'russian':
        text = normalise_text(
            f'{text}Отличный выбор! Ты выбрал(а) ' +
            'сертификат:\n*' +
            context.chat_data['impression'] +
            '*\n\nВ какой форме хочешь получить его?'
        )
        buttons = [
            '📧 По электронной почте',
            '📨 В подарочной коробке',
            '‹ Выбрать другое впечатление',
            '« Вернуться в главное меню'
        ]
    else:
        text = normalise_text(
            f'{text}Great choice! You chose ' +
            'the certificate:\n*' +
            context.chat_data['impression'] +
            '*\n\nIn what form do you want to receive it?'
        )
        buttons = [
            '📧 By email',
            '📨 In a gift box',
            '‹ Choose a different impression',
            '« Back to main menu'
        ]

    keyboard = [
        [
            InlineKeyboardButton(buttons[0], callback_data='email'),
            InlineKeyboardButton(buttons[1], callback_data='gift_box'),
        ],
        [
            InlineKeyboardButton(buttons[2], callback_data='impression')
        ],
        [
            InlineKeyboardButton(buttons[3], callback_data='main_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return SELECTING_RECEIVING_METHOD


async def handle_receiving_methods_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Receipt method selecting."""
    query = update.callback_query
    if not query:
        if context.chat_data['language'] == 'russian':
            text = (
                'Извини, непонятно, какой способ получения сертификата ты '
                'хочешь выбрать. Попробуй выбрать ещё раз.\n\n'
            )
        else:
            text = (
                "Sorry, it's not clear which method of receiving "
                'your certificate you want to choose. '
                'Try choosing again.\n\n'
            )

        next_state = await send_receiving_methods_menu(update, context, text)
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
    context.chat_data['delivery'] = 'email'
    if context.chat_data['language'] == 'russian':
        text = 'Напиши почту, на которую хотел(а) бы получить сертификат:'
    else:
        text = (
            'Write the email to which you would like to receive '
            'the certificate:'
        )
    await update.callback_query.edit_message_text(text=text)
    return WAITING_EMAIL


async def handle_email_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the WAITING_EMAIL state."""
    pattern = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    match = re.match(pattern, update.message.text.strip())
    if not match:
        if context.chat_data['language'] == 'russian':
            text = (
                'Ошибка в написании электронной почты.\n'
                'Пожалуйста, пришли нам свой адрес электронной почты:'
            )
        else:
            text = 'Email spelling error.\nPlease send us your email:'

        await update.message.reply_text(text=text)
        return WAITING_EMAIL

    context.chat_data['email'] = match.groups()[0]
    next_state = await send_privacy_policy(update, context)
    return next_state


async def handle_gift_box_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Gift-box button click."""
    context.chat_data['delivery'] = 'gift_box'
    next_state = await send_privacy_policy(update, context)
    return next_state


async def send_privacy_policy(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Send Privacy Policy to chat."""
    policy_url = await Database.get_policy_url(context.chat_data['language'])
    if context.chat_data['language'] == 'russian':
        text = (
            'Спасибо, записали 👌\n\n'
            'Пожалуйста, ознакомься с *[Политикой конфиденциальности и '
            f'положением об обработке персональных данных 📇]({policy_url})*'
        )
        button = 'Ознакомлен(а)'
    else:
        text = (
            'Thank you, we wrote it down 👌\n\n'
            'Please read the *[Privacy Policy and the provisions '
            f'on the processing of personal data 📇]({policy_url})*'
        )
        button = 'Acquainted'

    keyboard = [[InlineKeyboardButton(button, callback_data='privacy_policy')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text=text,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )
    return ACQUAINTED_PRIVACY_POLICY


async def handle_privacy_policy_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle Privacy Policy button click."""
    if context.chat_data['language'] == 'russian':
        text = 'Введи, пожалуйста, свои фамилию и имя (кириллицей):'
    else:
        text = 'Please write your first and last name:'
    await update.callback_query.edit_message_text(text=text)
    return WAITING_FULLNAME


async def handle_fullname_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the WAITING_FULLNAME state."""
    fullname = update.message.text.strip()
    if len(fullname) < 4 or ' ' not in fullname:
        if context.chat_data['language'] == 'russian':
            text = (
                'Ошибка в написании фамилии и имени.\n'
                'Пожалуйста, пришли нам свои фамилию и имя (кириллицей):'
            )
        else:
            text = (
                'First and last name spelling error.\n'
                'Please send us your first and last name:'
            )

        await update.message.reply_text(text=text)
        return WAITING_FULLNAME

    context.chat_data['fullname'] = fullname
    next_state = await send_phone_number_prompt(update, context)
    return next_state


async def send_phone_number_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Send prompt to enter phone number to chat."""
    if context.chat_data['language'] == 'russian':
        text = 'Оставь, пожалуйста, свой контактный номер телефона:'
    else:
        text = 'Please write your contact phone number:'

    await update.message.reply_text(text=text)
    return WAITING_PHONE_NUMBER


async def handle_phone_number_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle the WAITING_PHONE_NUMBER state."""
    value = update.message.text.strip()
    error = not bool(value)
    if not error:
        if value[0] == '8':
            value = '+7' + value[1:]

        try:
            value = phonenumbers.parse(value)
        except phonenumbers.phonenumberutil.NumberParseException:
            error = True

        if not error:
            error = not phonenumbers.is_valid_number(value)

    if error:
        if context.chat_data['language'] == 'russian':
            text = (
                'Введён некорректный номер телефона.\n'
                'Пожалуйста, пришли нам свой номер телефона:'
            )
        else:
            text = (
                'Phone number spelling error.\n'
                'Please send us your phone number:'
            )

        await update.message.reply_text(text=text)
        return WAITING_PHONE_NUMBER

    context.chat_data['phone_number'] = (
        f'+{value.country_code}{value.national_number}'
    )
    if context.chat_data['delivery'] == 'email':
        next_state = await send_payment_details(update, context)
        return next_state

    next_state = await send_delivery_methods_menu(update, context)
    return next_state


async def send_payment_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = ''
) -> int:
    """Send Payment details and wait for payment screenshot."""
    payment_details = await Database.get_payment_details(
        context.chat_data['language']
    )
    payment_details = normalise_text(payment_details)
    if context.chat_data['language'] == 'russian':
        text = (
            text +
            'Оплатить покупку можно по указанным реквизитам:\n\n*' +
            payment_details +
            '\n\n*После оплаты отправь нам скриншот с подтверждением оплаты:'
        )
    else:
        text = (
            text +
            'You can pay for the purchase by the specified details:\n\n*' +
            payment_details +
            '\n\n*After payment, send us a screenshot with payment:'
            'confirmation'
        )
    await update.message.reply_text(text=text, parse_mode='MarkdownV2')
    return WAITING_PAYMENT_SCREENSHOT


async def handle_payment_screenshot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Process receipt of screenshot of payment."""
    if not update.message.photo:
        if context.chat_data['language'] == 'russian':
            text = 'Ты прислал не скриншот оплаты.\n\n'
        else:
            text = (
                "You didn't send a screenshot "
                "of the payment.n\n"
            )
        await send_payment_details(update, context, text)

    photo_id = update.message.photo[-1].file_id
    screenshot_file = context.bot.get_file(photo_id)
    screenshot_file.download('screenshot.jpg')

    if context.chat_data['language'] == 'russian':
        text = (
            'Спасибо за покупку! Мы всё проверим '
            'и в ближайшее время тебе напишет оператор 🎆'
        )
        button = 'Спасибо 👌'
    else:
        text = (
            'Thank you for your purchase! We will check everything '
            'and an operator will write to you shortly 🎆'
        )
        button = 'Thanks 👌'

    keyboard = [[InlineKeyboardButton(button, callback_data='dialogue_end')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )
    return DIALOGUE_END


async def handle_dialogue_end(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle end of dialogue."""
    pass


async def send_delivery_methods_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Send Delivery methods menu."""
    pass


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
