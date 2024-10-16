from aiogram import Router

from src.bot.filters.order_filter import OrderFilter

order_router = Router(name='order')
order_router.message.filter(OrderFilter())
