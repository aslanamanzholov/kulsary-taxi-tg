import emoji
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BACK_OR_MASSEUSES = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Назад {emoji.emojize(':BACK_arrow:')}"),
         KeyboardButton(text=f"Мастерицы {emoji.emojize(':smiling_face_with_halo:')}")],
    ],
    resize_keyboard=True
)

BACK_MASSEUSE_BUTTON = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"Назад {emoji.emojize(':BACK_arrow:')}"),
         KeyboardButton(text=f"Мастерицы {emoji.emojize(':smiling_face_with_halo:')}")]
    ],
    resize_keyboard=True
)

RATE_MASSEUSE_BUTTONS = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=f"{emoji.emojize(':star:')}")],
        [KeyboardButton(text=f"{emoji.emojize(':star:')}{emoji.emojize(':star:')}")],
        [KeyboardButton(text=f"{emoji.emojize(':star:')}{emoji.emojize(':star:')}{emoji.emojize(':star:')}")],
        [KeyboardButton(text=f"{emoji.emojize(':star:')}{emoji.emojize(':star:')}{emoji.emojize(':star:')}"
                             f"{emoji.emojize(':star:')}")],
        [KeyboardButton(text=f"{emoji.emojize(':star:')}{emoji.emojize(':star:')}{emoji.emojize(':star:')}"
                             f"{emoji.emojize(':star:')}{emoji.emojize(':star:')}")],
        [KeyboardButton(text=f"Отмена")],

    ],
    resize_keyboard=True
)
