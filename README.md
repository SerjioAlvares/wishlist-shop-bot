# Telegram-бот для продаж сертификатов впечатлений

Проект представляет Telegram-бота для продаж сертификатов впечатлений.

## Как установить

Для запуска бота нужен Python версии 3.8+.

Скачайте код c Github. Создайте виртуальное окружение и активируйте его:

В Windows:
```ssh
python -m venv venv
venv\Scripts\activate
```

В Linux:
```ssh
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:

В Windows:
```ssh
pip install -r requirements.txt
```

В Linux:
```ssh
pip3 install -r requirements.txt
```

## Переменные окружения

Часть настроек утилит берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в той же папке, где и скрипты, и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступна следующая обязательная переменная окружения:

- `TELEGRAM_BOT_TOKEN` - API-токен Telegram-бота. Если такого telegram-бота пока нет, [создайте его](https://way23.ru/регистрация-бота-в-telegram.html).

Пример содержимого файла .env:
```
#
TELEGRAM_BOT_TOKEN=958423683:AAEAtJ5Lde5YYfkjergber
```

## Как запустить

Для запуска бота откройте консоль `cmd` в Windows или терминал в Linux и наберите в командной строке команду:

В Windows:
```ssh
python bot.py
```

В Linux:
```ssh
python3 bot.py
```

## Схема чат-бота

```mermaid
flowchart TB
    %% Documentation: https://mermaid-js.github.io/mermaid/#/flowchart
    A(("/start")):::entryPoint -->|Выбери, пожалуйста, язык / Please, select language| B((SELECTING_LANGUAGE)):::state
    B --> |" - Ru <br /> - Eng <br />"|C("(choice)"):::userInput
    classDef userInput  fill:#2a5279, color:#ffffff, stroke:#ffffff
    classDef state fill:#222222, color:#ffffff, stroke:#ffffff
    classDef entryPoint fill:#009c11, stroke:#42FF57, color:#ffffff
    classDef termination fill:#bb0007, stroke:#E60109, color:#ffffff
```

## Цель проекта

Код написан для реального заказа на фрилансе.
