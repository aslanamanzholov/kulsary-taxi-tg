import emoji

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MASSEUSE_MAIN_BUTTONS_MARKUP = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=emoji.emojize(":red_heart:")),
         KeyboardButton(text=emoji.emojize(":thumbs_down:"))]
    ],
    resize_keyboard=True
)

CANCEL_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

SHARE_PHONE_OR_CANCEL_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поделиться номером телефона", request_contact=True), KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)

CANCEL_WITHOUT_IMAGE_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Без изображений")],
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)