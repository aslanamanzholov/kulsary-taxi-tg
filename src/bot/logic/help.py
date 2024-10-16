from aiogram import Router, types
from aiogram.filters import Command

from src.bot.structures.keyboards.menu import MENU_KEYBOARD

help_router = Router(name='help')


@help_router.message(Command(commands='help'))
async def help_handler(message: types.Message):
    """Help command handler."""
    return await message.answer("Байланысу үшін осы сілтемеге өтіңіз: https://t.me/amanzholovaslan", reply_markup=MENU_KEYBOARD)
