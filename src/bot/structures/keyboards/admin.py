import emoji
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

ADMIN_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=emoji.emojize("Создать анкету")),
            KeyboardButton(text=emoji.emojize("Мои объявления"))
        ]
    ],
    resize_keyboard=True
)
