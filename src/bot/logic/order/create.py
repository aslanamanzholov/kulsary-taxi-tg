import emoji
import requests
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.bot.structures.fsm.order import OrderCreateGroup
from .router import order_router

from src.bot.structures.keyboards.order import CANCEL_BUTTON
from src.bot.structures.keyboards.menu import MENU_KEYBOARD


@order_router.message(OrderCreateGroup.image)
async def register_masseuse_image_handler(message: Message, state: FSMContext):
    photo = message.photo[-2]
    file_id = photo.file_id

    images = state.get("images", [])
    images.append(file_id)

    await state.update_data(images=images)
    await state.set_state(OrderCreateGroup.name)

    reply_markup = CANCEL_BUTTON
    response_text = f'Имя мастерицы {emoji.emojize(":smiling_face_with_halo:")}'
    return await message.answer(response_text, reply_markup=reply_markup)


@order_router.message(OrderCreateGroup.name)
@order_router.message(OrderCreateGroup.address)
@order_router.message(OrderCreateGroup.actually_address)
@order_router.message(OrderCreateGroup.price)
async def register_masseuse_data_handler(message: Message, state: FSMContext):
    state_key = message.text.lower()

    await state.update_data(**{state_key: message.text})

    next_state = OrderCreateGroup.next_state(OrderCreateGroup[state_key])
    reply_markup = CANCEL_BUTTON

    if next_state:
        response_text = f"Введите {next_state.value} {emoji.emojize(':house_with_garden:')}"
    else:
        await process_masseuse_data(message, state)
        return

    return await message.answer(response_text, reply_markup=reply_markup)


async def process_masseuse_data(message: Message, state: FSMContext):
    data = await state.get_data()

    masseuse_image = data.get('images', [])

    for image in masseuse_image:
        photo_file = await message.bot.get_file(image)
        photo_url = photo_file.file_path
        request_url = f"https://api.telegram.org/file/bot{getenv('BOT_TOKEN')}/{photo_url}"

        try:
            response = requests.get(request_url)
            response.raise_for_status()
            masseuse_image = response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image: {e}")
            masseuse_image = None
            break

    await db.masseuse.new(
        user_id=message.from_user.id,
        username=message.from_user.username,
        image=masseuse_image,
        **data
    )

    await state.clear()

    response_text = f'Ваша анкета находится в разделе "Мастерицы" {emoji.emojize(":slightly_smiling_face:")}'
    reply_markup = MENU_KEYBOARD

    return await message.answer(response_text, reply_markup=reply_markup)
