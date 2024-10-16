from os import getenv

import emoji
import requests
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .router import order_router
from ...structures.fsm.order import OrderEditGroup
from ...structures.keyboards.order import CANCEL_BUTTON, CANCEL_WITHOUT_IMAGE_BUTTON
from ...structures.keyboards.menu import MENU_KEYBOARD


@order_router.message(F.text.lower().startswith('менің сапарларым'))
async def process_get_orders_command(message: types.Message, db):
    orders_of_user = await db.taxi_ride.get_rides_by_passenger_id(passenger_id=message.from_user.id)
    if orders_of_user:
        for order in orders_of_user:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Өзгерту', callback_data=f'edit_order {order.id}')],
                    [InlineKeyboardButton(text='Жою', callback_data=f'delete_order {order.id}')]
                ]
            )
            text = (f"\n*Жүргізуші*: {order.driver_id}\n"
                    f"*А точкасы*: {order.start_location}\n"
                    f"*Б точкасы*: {order.actually_address if order.status == 'completed' else 'Сапар аякталмаган'}\n"
                    f"*Баға*: {order.price}тг\n")
            return await message.answer(text, reply_markup=reply_markup, parse_mode='MARKDOWN')
    else:
        return await message.answer("Ой, бірақ сізде сапар жоқ :(",
                                    reply_markup=MENU_KEYBOARD)

@order_router.callback_query(F.data.startswith("edit_order"))
async def order_edit_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    order_id = callback_query.data.split(' ')[1] or None
    await state.set_state(OrderEditGroup.name)
    await state.update_data(order_id=order_id)
    return await callback_query.message.answer(
        f'{emoji.emojize(":speech_balloon:")} Мастерица атын қалай өзгерту керектігін жазыңыз:',
        reply_markup=CANCEL_BUTTON,
    )

@order_router.message(OrderEditGroup.name)
async def edit_order_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderEditGroup.image)
    return await message.answer(f"Мастерица суретін жіберіңіз", reply_markup=CANCEL_WITHOUT_IMAGE_BUTTON)

@order_router.message(OrderEditGroup.image)
async def edit_order_image_handler(message: types.Message, state: FSMContext):
    photo = message.photo[-2]
    file_id = photo.file_id
    await state.update_data(image=[file_id])
    await state.set_state(OrderEditGroup.address)
    return await message.answer(
        f"Жұмыс мекенжайын енгізіңіз (мысалы: Гоголя/Зенкова) өзгерту үшін "
        f"{emoji.emojize(':house_with_garden:')}",
        reply_markup=CANCEL_BUTTON
    )

@order_router.message(OrderEditGroup.address)
async def edit_order_address_handler(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderEditGroup.actually_address)
    return await message.answer(
        f"Нақты мекенжайын енгізіңіз (мысалы: Толе би 189) өзгерту үшін "
        f"{emoji.emojize(':house_with_garden:')}",
        reply_markup=CANCEL_BUTTON
    )

@order_router.message(OrderEditGroup.actually_address)
async def edit_order_address_handler(message: types.Message, state: FSMContext):
    await state.update_data(actually_address=message.text)
    await state.set_state(OrderEditGroup.price)
    return await message.answer(
        'Сіз өзгерту үшін массаж бағасын көрсетіңіз', reply_markup=CANCEL_BUTTON
    )

@order_router.message(OrderEditGroup.price)
async def edit_order_address_handler(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(OrderEditGroup.description)
    return await message.answer(
        'Мастерица сипаттамасын жазыңыз (жасы, бойы, мүмкіндігінше қосымша қызметтер, жеңілдіктер және т.б.)',
        reply_markup=CANCEL_BUTTON
    )

@order_router.message(OrderEditGroup.description)
async def edit_user_order_handler(message: types.Message, state: FSMContext, db):
    data = await state.update_data(description=message.text)
    order = await db.order.get_order_by_id(int(data['order_id']))
    order_image = data['image']
    if order_image:
        for image in order_image:
            photo_file = await message.bot.get_file(image)
            photo_url = photo_file.file_path
            request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"
            response = requests.get(request_url)
            if response.status_code == 200:
                order_image = response.content
    order.name = data['name']
    order.image = order_image
    order.address = data['address']
    order.actually_address = data['actually_address']
    order.price = data['price']
    order.description = data['description']
    await db.session.commit()
    await state.clear()
    return await message.answer(
        '*Сіз хабарландыру мазмұнын сәтті жаңарттыңыз*', reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN"
    )

@order_router.callback_query(F.data.startswith("delete_order"))
async def order_delete_callback_handler(callback_query: types.CallbackQuery, db):
    order_id = callback_query.data.split(' ')[1] or None
    order = await db.order.get_order_by_id(int(order_id))
    if order:
        await db.session.delete(order)
        await db.session.commit()
        return await callback_query.message.answer("*Анкета сәтті жойылды*", parse_mode='MARKDOWN')
    else:
        return await callback_query.message.answer("*Анкетаны таба алмадым :(*", parse_mode='MARKDOWN')
