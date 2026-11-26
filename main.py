import os
from collections import defaultdict

import telebot
from telebot import types


GAMES = {
    "gta": ("GTA V", 645),
    "fallout": ("Fallout 76", 479),
    "pubg": ("PUBG", 379),
}


def create_bot(token):
    bot = telebot.TeleBot(token)
    baskets = defaultdict(list)

    @bot.message_handler(commands=["start", "help"])
    def show_help(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row("/games", "/basket")
        keyboard.row("/help", "/info", "/stop")
        bot.send_message(
            message.chat.id,
            "Учебный каталог игр. /games открывает каталог, /basket показывает корзину.",
            reply_markup=keyboard,
        )

    @bot.message_handler(commands=["info"])
    def show_info(message):
        bot.send_message(message.chat.id, "Учебный Telegram-бот с каталогом и корзиной.")

    @bot.message_handler(commands=["stop"])
    def stop(message):
        bot.send_message(message.chat.id, "До встречи!", reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(commands=["games"])
    def show_games(message):
        for code, (title, price) in GAMES.items():
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton("В корзину", callback_data=f"add:{code}"))
            bot.send_message(message.chat.id, f"{title} — {price} ₽", reply_markup=keyboard)

    @bot.message_handler(commands=["basket"])
    def show_basket(message):
        items = [GAMES[code] for code in baskets.get(message.chat.id, [])]
        lines = [f"{title} — {price} ₽" for title, price in items]
        text = "\n".join(lines + [f"Итого: {sum(price for _, price in items)} ₽"]) if items else "Корзина пуста."
        bot.send_message(message.chat.id, text)

    @bot.callback_query_handler(func=lambda call: bool(call.data and call.data.startswith("add:")))
    def add_to_basket(call):
        code = call.data.removeprefix("add:")
        if call.message and code in GAMES:
            baskets[call.message.chat.id].append(code)
            bot.answer_callback_query(call.id, "Добавлено в корзину.")
        else:
            bot.answer_callback_query(call.id, "Позиция недоступна.")

    return bot


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("Укажите TELEGRAM_BOT_TOKEN в окружении.")
    create_bot(token).infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()
