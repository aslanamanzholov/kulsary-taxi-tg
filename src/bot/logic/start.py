"""This file represents a start logic."""
import emoji
from aiogram import Router, types
from aiogram.filters import CommandStart

from src.bot.structures.keyboards.admin import ADMIN_MAIN_BUTTONS_MARKUP
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.configuration import conf

start_router = Router(name='start')


@start_router.message(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user.id in conf.admin_ids:
        return await message.answer(f'Вы авторизовались как администратор!', reply_markup=ADMIN_MAIN_BUTTONS_MARKUP)
    else:
        welcome_text = (
            f'Сәлем, KulsaryTaxi-ге қош келдіңіз! {emoji.emojize(":taxi:")}\n'
            'Бекітілген бағамен қауіпсіз әрі ыңғайлы такси қызметін ұсынамыз.\n\n'
            f'Бағалар: {emoji.emojize(":money_bag:")}\n'
            '- Эконом: 600-800тг, тиімді бағамен сапар.\n'
            '- Комфорт: 800-1000тг, ыңғайлы және жайлы сапар.\n\n'
            f'Не істей аласыз:\n'
            '- Такси шақыру үшін /order_taxi командасын, немесе төмендегі батырманы басыңыз.\n'
            '- Жүргізуші ретінде тіркелу үшін /register_driver командасын пайдаланыңыз.\n'
            '- Өз тапсырыстарыңызды көру үшін /my_orders командасын жазыңыз.\n'
            '- Кез келген сұрақтарыңыз болса, /help командасын, немесе Көмек батырмасын басуыңызға болады!\n\n'
            f'Сапарыңыз сәтті болсын! {emoji.emojize(":motorway:")}'
        )
        await message.answer(welcome_text, reply_markup=MENU_KEYBOARD)
