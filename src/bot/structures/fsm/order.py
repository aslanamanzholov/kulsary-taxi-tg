from aiogram.fsm.state import StatesGroup, State


class OrderCreateGroup(StatesGroup):
    name = State()
    image = State()
    description = State()
    address = State()
    actually_address = State()
    price = State()


class OrderClientLikeGroup(StatesGroup):
    time = State()
    phone = State()


class OrderEditGroup(StatesGroup):
    name = State()
    image = State()
    description = State()
    address = State()
    actually_address = State()
    price = State()
