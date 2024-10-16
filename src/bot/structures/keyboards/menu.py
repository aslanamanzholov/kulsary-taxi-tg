import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Такси шақыру"), KeyboardButton(text="Менің сапарларым")],
        [KeyboardButton(text="Көмек"), KeyboardButton(text="Жүргізуші болу")]
    ],
    resize_keyboard=True
)