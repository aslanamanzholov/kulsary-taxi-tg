"""This file represents a Order logic."""
import datetime
import emoji

from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.structures.keyboards.order import MASSEUSE_MAIN_BUTTONS_MARKUP, CANCEL_BUTTON, \
    SHARE_PHONE_OR_CANCEL_BUTTON
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.configuration import conf

from .router import order_router
from src.bot.structures.fsm.order import OrderCreateGroup, OrderClientLikeGroup

current_record = {}


@order_router.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        f"Вы отменили {emoji.emojize(':crying_face:')}", reply_markup=MENU_KEYBOARD,
    )


async def calculate_avg_rate(feedback_rate_list, feedback_count):
    try:
        return round(sum(feedback_rate_list) / feedback_count)
    except ZeroDivisionError:
        return 0


async def masseuse_view_func(masseuse, message, db):
    if masseuse:
        feedback_count = await db.feedback.get_masseuse_feedback_count_by_masseuse_id(masseuse_id=masseuse.id)
        feedback_rate_list = await db.feedback.get_masseuse_feedback_rate_list_by_masseuse_id(masseuse_id=masseuse.id)
        avg_rate = await calculate_avg_rate(feedback_rate_list, feedback_count)
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f'Отзывы({feedback_count})',
                                         callback_data=f"feedback_callback_{masseuse.id}"),
                ],
                [
                    InlineKeyboardButton(text='Написать отзыв', callback_data=f"create_feedback_{masseuse.id}"),
                ]
            ]
        )
        text = (f"*Рейтинг*: {emoji.emojize(':star:') * avg_rate if avg_rate != 0 else 'Отсутствует'}\n"
                f"*Мастерица*: {masseuse.name}\n"
                f"*Адрес*: {masseuse.address}\n"
                f"*Массаж*: от {masseuse.price}тг\n"
                f"*Детали*: {masseuse.description}\n"
                f"*Проверена* {emoji.emojize(':check_mark_button:')}\n")
        if masseuse.image:
            await message.bot.send_photo(message.chat.id,
                                         types.BufferedInputFile(masseuse.image,
                                                                 filename=f"user_photo_{masseuse.id}.png"),
                                         caption=text,
                                         reply_markup=reply_markup,
                                         parse_mode='MARKDOWN')
            return await message.answer(f"Вы также можете выбрать одно из следующих действий: "
                                        f"{emoji.emojize(':backhand_index_pointing_down:')}",
                                        reply_markup=MASSEUSE_MAIN_BUTTONS_MARKUP,
                                        parse_mode='MARKDOWN')
        else:
            await message.answer(text, reply_markup=reply_markup, parse_mode='MARKDOWN')
            return await message.answer(text, reply_markup=MASSEUSE_MAIN_BUTTONS_MARKUP, parse_mode='MARKDOWN')
    else:
        current_record.clear()
        text = f'На данный момент нет доступных мастериц {emoji.emojize(":smiling_face_with_tear:")}'
        return await message.answer(text, reply_markup=MENU_KEYBOARD)


@order_router.message(F.text.lower().startswith('создать анкету'))
async def process_create_command(message: types.Message, state: FSMContext):
    if message.from_user.id in conf.admin_ids:
        await state.set_state(OrderCreateGroup.image)
        return await message.answer(
            'Пришлите фотографию мастерицы', reply_markup=CANCEL_BUTTON,
        )
    else:
        return await message.answer(f'Вы не администратор {emoji.emojize(":frowning_face:")}',
                                    reply_markup=MENU_KEYBOARD)


@order_router.message(F.text.lower() == emoji.emojize(":red_heart:"))
async def process_like_command(message: types.Message, state: FSMContext):
    custom_inline_keyboard = []
    now = datetime.datetime.now()
    time_options = [now + datetime.timedelta(minutes=30 * i - now.minute % 30) for i in range(1, 7)]
    for time_option in time_options:
        button_text = time_option.strftime("%H:%M")
        callback_data = f"select_time_{time_option.strftime('%H:%M')}"
        custom_inline_keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=custom_inline_keyboard)
    await state.set_state(OrderClientLikeGroup.time)
    await message.answer("Выберите удобное время:", reply_markup=keyboard, parse_mode="MARKDOWN")
    return await message.answer("Вы можете *Отменить бронь* по кнопке ниже:",
                                reply_markup=CANCEL_BUTTON,
                                parse_mode="MARKDOWN")


@order_router.message(OrderClientLikeGroup.time)
@order_router.callback_query(F.data.startswith("select_time"))
async def select_time_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    selected_time = callback_query.data.split('_')[2]
    await state.update_data(time=selected_time)
    await state.set_state(OrderClientLikeGroup.phone)
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    return await callback_query.message.answer(text="Укажите, *номер телефона* для подтверждения времени",
                                               reply_markup=SHARE_PHONE_OR_CANCEL_BUTTON, parse_mode="MARKDOWN")


@order_router.message(OrderClientLikeGroup.phone)
async def process_client_phone_handler(message: types.Message, state: FSMContext, db):
    if message.contact:
        data = await state.update_data(phone=message.contact.phone_number)
    else:
        data = await state.update_data(phone=message.text)
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    masseuse = await db.masseuse.get_masseuse(offset=offset)
    client_time = data.get('time', None)
    client_phone = data.get('phone', None)
    author_id = masseuse.user_id if masseuse else None
    if author_id:
        client_username_id = message.from_user.username if message.from_user.username else message.from_user.id
        chat_id = message.chat.id
        notification_message = (f"Забронирована время на мастерицу *{masseuse.name}* в *{client_time}*\n"
                                f"Позвоните на номер *{client_phone}* "
                                f"или напишите в Telegram *https://t.me/{client_username_id}*\n")

        approve_callback_data = f"{chat_id}_{masseuse.id}_{client_phone}_{client_time}"
        disapprove_callback_data = f"{chat_id}_{masseuse.id}"

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Одобрить заявку',
                                         callback_data=f"approve_client_{approve_callback_data}"),
                    InlineKeyboardButton(text='Отклонить заявку',
                                         callback_data=f"disapprove_client_{disapprove_callback_data}")
                ]
            ]
        )

        await message.bot.send_message(author_id, notification_message, reply_markup=reply_markup,
                                       parse_mode="MARKDOWN")
    await db.masseuse_client_record.new(
        client_user_id=message.from_user.id,
        client_username=message.from_user.username,
        masseuse_user_id=author_id,
        masseuse_username=masseuse.username,
        client_time=client_time,
        client_phone=client_phone,
        masseuse_name=masseuse.name,
        success=True
    )
    await state.clear()
    return await message.answer(
        text=f"В течение 1-5 минут вам позвонят для подтверждения времени.{emoji.emojize(':see-no-evil_monkey:')}",
        reply_markup=MENU_KEYBOARD)


@order_router.message(F.text.lower().startswith('мастерицы'))
@order_router.message(Command(commands='masseuse'))
async def process_masseuse_handler(message: types.Message, db):
    current_record.clear()
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    masseuse = await db.masseuse.get_masseuse(offset=offset)
    return await masseuse_view_func(masseuse, message, db)


@order_router.message(F.text.lower() == emoji.emojize(":thumbs_down:"))
async def process_dislike_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1
    masseuse = await db.masseuse.get_masseuse(offset=offset + 1)
    return await masseuse_view_func(masseuse, message, db)


@order_router.message(F.text.lower().startswith(emoji.emojize(':love_letter:')))
async def process_sleep_command(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    current_record[user_id] = offset + 1
    masseuse = await db.masseuse.get_masseuse(offset=offset)
    masseuse_username_id = masseuse.username if masseuse.username else masseuse.user_id
    return await message.answer(f"Вот профиль мастерицы: https://t.me/{masseuse_username_id}",
                                reply_markup=MENU_KEYBOARD)


@order_router.callback_query(F.data.startswith("payed"))
async def payed_client_callback_handler(callback_query: types.CallbackQuery, db):
    masseuse_id = callback_query.data.split('_')[1]
    client_phone = callback_query.data.split('_')[2]
    client_time = callback_query.data.split('_')[3]
    masseuse = await db.masseuse.get_masseuse_by_id(masseuse_id=masseuse_id)
    masseuse_name = masseuse.name
    await callback_query.bot.send_message(masseuse.user_id, f"Клиент с номером "
                                                            f"*{client_phone}* по времени в *{client_time}* в пути "
                                                            f"к мастерице *{masseuse_name}*.",
                                          reply_markup=MENU_KEYBOARD,
                                          parse_mode="MARKDOWN")
    return await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    # await callback_query.message.answer(text=f'Мастерица *{masseuse_name}* ждет вас в *{client_time}* по '
    #                                          f'адресу *{masseuse.address}* {emoji.emojize(":face_blowing_a_kiss:")}',
    #                                     reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")


@order_router.callback_query(F.data.startswith("cancel_pay"))
async def cancel_pay_client_callback_handler(callback_query: types.CallbackQuery, db):
    masseuse_id = callback_query.data.split('_')[2]
    client_phone = callback_query.data.split('_')[3]
    client_time = callback_query.data.split('_')[4]
    masseuse = await db.masseuse.get_masseuse_by_id(masseuse_id=masseuse_id)
    masseuse_name = masseuse.name
    await callback_query.bot.send_message(masseuse.user_id,
                                          f"Бронь на мастерицу {masseuse_name} была отменена клиентом по номеру "
                                          f"{client_phone} на время в {client_time} {emoji.emojize(':pensive_face:')}",
                                          reply_markup=MENU_KEYBOARD,
                                          parse_mode="MARKDOWN")
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    return await callback_query.message.answer(text=f'Вы отменили бронь {emoji.emojize(":pensive_face:")}',
                                               reply_markup=MENU_KEYBOARD)


@order_router.callback_query(F.data.startswith("disapprove_client"))
async def disapprove_client_callback_handler(callback_query: types.CallbackQuery, db):
    chat_id = callback_query.data.split('_')[2]
    masseuse_id = callback_query.data.split('_')[3]
    masseuse = await db.masseuse.get_masseuse_by_id(masseuse_id=masseuse_id)
    await callback_query.bot.send_message(chat_id=chat_id,
                                          text=f"К-сожалению вам отказали в услуге мастерицы "
                                               f"*{masseuse.name},* "
                                               f"попробуйте выбрать другую мастерицу "
                                               f"{emoji.emojize(':pensive_face:')}",
                                          reply_markup=MENU_KEYBOARD, parse_mode="MARKDOWN")
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    return await callback_query.message.answer(text='Вы отклонили заявку', reply_markup=MENU_KEYBOARD)


@order_router.callback_query(F.data.startswith("approve_client"))
async def approve_client_callback_handler(callback_query: types.CallbackQuery, db):
    chat_id = callback_query.data.split('_')[2]
    masseuse_id = callback_query.data.split('_')[3]
    client_phone = callback_query.data.split('_')[4]
    client_time = callback_query.data.split('_')[5]
    masseuse = await db.masseuse.get_masseuse_by_id(masseuse_id=masseuse_id)
    callback_data = f"{masseuse_id}_{client_phone}_{client_time}"

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'OK {emoji.emojize(":OK_hand:")}',
                                     callback_data=f"payed_{callback_data}"),
                InlineKeyboardButton(text=f'Отменить бронь {emoji.emojize(":man_gesturing_NO:")}',
                                     callback_data=f"cancel_pay_{callback_data}")
            ]
        ]
    )
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )

    await callback_query.message.bot.send_message(chat_id=chat_id,
                                                  text=f"Мастерица *{masseuse.name}* вас ждет "
                                                       f"в *{client_time}* по адресу "
                                                       f"*{masseuse.actually_address if masseuse.actually_address else masseuse.address}* "
                                                       f"{emoji.emojize(':face_blowing_a_kiss:')}",
                                                  reply_markup=reply_markup, parse_mode="MARKDOWN")
    return await callback_query.message.answer(text='Вы одобрили заявку', reply_markup=MENU_KEYBOARD)
