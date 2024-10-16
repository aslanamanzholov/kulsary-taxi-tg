import emoji
from aiogram import F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.logic.order import current_record, masseuse_view_func
from .router import order_router
from src.bot.structures.keyboards.feedback import BACK_OR_MASSEUSES, RATE_MASSEUSE_BUTTONS
from src.bot.structures.fsm.feedback import MasseuseFeedbackCreateGroup
from src.bot.structures.keyboards.menu import MENU_KEYBOARD
from src.bot.structures.keyboards.order import CANCEL_BUTTON

current_feedback = {}


@order_router.callback_query(F.data.startswith("feedback_callback"))
async def feedback_callback_handler(callback_query: types.CallbackQuery, db):
    masseuse_id = callback_query.data.split('_')[2]
    current_feedback.clear()
    user_id = callback_query.message.from_user.id
    offset = current_record.get(user_id, 0)
    feedback = await db.feedback.get_masseuse_feedback_by_masseuse_id(masseuse_id=masseuse_id, offset=offset)
    if feedback:
        feedback_reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{emoji.emojize(':left_arrow:')}",
                                      callback_data=f'left_arrow_{masseuse_id}'),
                 InlineKeyboardButton(text=f"{emoji.emojize(':right_arrow:')}",
                                      callback_data=f'right_arrow_{masseuse_id}')]
            ]
        )
        text = (f"\n*Отзыв*\n\n"
                f"*Рейтинг*: {0 if feedback.rate == 0 else emoji.emojize(':star:') * feedback.rate}\n"
                f"*Описание*: {feedback.text}\n\n")
        await callback_query.message.answer(text=text, reply_markup=feedback_reply_markup, parse_mode="MARKDOWN")
        return await callback_query.message.answer(text=f"Вы также можете выбрать одно из следующих действий: "
                                                        f"{emoji.emojize(':backhand_index_pointing_down:')} ",
                                                   reply_markup=BACK_OR_MASSEUSES, parse_mode="MARKDOWN")
    else:
        return await callback_query.message.answer(text=f"*К-сожалению у данной мастерицы отсутствуют отзывы* "
                                                        f"{emoji.emojize(':crying_face:')}",
                                                   reply_markup=BACK_OR_MASSEUSES,
                                                   parse_mode="MARKDOWN")


@order_router.callback_query(F.data.startswith('left_arrow'))
async def process_next_feedback_command(callback_query: types.CallbackQuery, db):
    try:
        masseuse_id = callback_query.data.split('_')[2]
        user_id = callback_query.message.from_user.id
        offset = current_feedback.get(user_id, 0)
        if offset > 0:
            current_feedback[user_id] = offset - 1
            feedback = await db.feedback.get_masseuse_feedback_by_masseuse_id(masseuse_id=masseuse_id,
                                                                              offset=offset - 1)
            if feedback:
                feedback_reply_markup = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=f"{emoji.emojize(':left_arrow:')}",
                                              callback_data=f'left_arrow_{masseuse_id}'),
                         InlineKeyboardButton(text=f"{emoji.emojize(':right_arrow:')}",
                                              callback_data=f'right_arrow_{masseuse_id}')]
                    ]
                )
                text = (f"\n*Отзыв*\n\n"
                        f"*Рейтинг*: {0 if feedback.rate == 0 else emoji.emojize(':star:') * feedback.rate}\n"
                        f"*Описание*: {feedback.text}\n\n")
                return await callback_query.message.edit_text(text=text, reply_markup=feedback_reply_markup,
                                                       parse_mode="MARKDOWN")
    except TelegramBadRequest:
        pass


@order_router.callback_query(F.data.startswith('right_arrow'))
async def process_next_feedback_command(callback_query: types.CallbackQuery, db):
    masseuse_id = callback_query.data.split('_')[2]
    user_id = callback_query.message.from_user.id
    offset = current_feedback.get(user_id, 0)
    if offset >= 0:
        current_feedback[user_id] = offset + 1
        feedback = await db.feedback.get_masseuse_feedback_by_masseuse_id(masseuse_id=masseuse_id, offset=offset + 1)
        if feedback:
            feedback_reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"{emoji.emojize(':left_arrow:')}",
                                          callback_data=f'left_arrow_{masseuse_id}'),
                     InlineKeyboardButton(text=f"{emoji.emojize(':right_arrow:')}",
                                          callback_data=f'right_arrow_{masseuse_id}')]
                ]
            )
            text = (f"\n*Отзыв*\n\n"
                    f"*Рейтинг*: {0 if feedback.rate == 0 else emoji.emojize(':star:') * feedback.rate}\n"
                    f"*Описание*: {feedback.text}\n\n")
            return await callback_query.message.edit_text(text=text, reply_markup=feedback_reply_markup, parse_mode="MARKDOWN")


@order_router.callback_query(F.data.startswith("create_feedback"))
async def process_write_feedback_command(callback_query: types.CallbackQuery, state: FSMContext, db):
    masseuse_id = callback_query.data.split('_')[2]
    masseuse = await db.masseuse.get_masseuse_by_id(masseuse_id=masseuse_id)
    await state.update_data(masseuse_id=int(masseuse_id))
    await state.set_state(MasseuseFeedbackCreateGroup.rate)
    return await callback_query.message.answer(
        f'Выберите кол-во звезд рейтинга для мастерицы *{masseuse.name}* '
        f'{emoji.emojize(":backhand_index_pointing_down:")}',
        reply_markup=RATE_MASSEUSE_BUTTONS,
        parse_mode='MARKDOWN'
    )


@order_router.message(MasseuseFeedbackCreateGroup.rate)
async def process_write_rate_command(message: types.Message, state: FSMContext):
    emoji_count = emoji.emoji_count(message.text)
    await state.update_data(rate=emoji_count)
    await state.set_state(MasseuseFeedbackCreateGroup.text)
    return await message.answer(
        f'Напишите ниже текст отзыва: {emoji.emojize(":backhand_index_pointing_down:")}',
        reply_markup=CANCEL_BUTTON,
    )


@order_router.message(MasseuseFeedbackCreateGroup.text)
async def process_write_text_command(message: types.Message, state: FSMContext, db):
    data = await state.update_data(text=message.text)
    await db.feedback.new(feedback_user_id=message.from_user.id,
                          feedback_username=message.from_user.username,
                          masseuse_id=data.get('masseuse_id', None),
                          rate=data.get('rate', None),
                          text=data.get('text', None))
    await state.clear()
    return await message.answer(
        f'Вы успешно написали отзыв о мастерице {emoji.emojize(":partying_face:")}'
        f'{emoji.emojize(":slightly_smiling_face:")}', reply_markup=MENU_KEYBOARD
    )


@order_router.message(F.text.lower().startswith('назад'))
async def process_back_button(message: types.Message, db):
    user_id = message.from_user.id
    offset = current_record.get(user_id, 0)
    masseuse = await db.masseuse.get_masseuse(offset=offset)
    return await masseuse_view_func(masseuse, message, db)
