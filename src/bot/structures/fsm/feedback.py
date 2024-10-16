from aiogram.fsm.state import StatesGroup, State


class MasseuseFeedbackCreateGroup(StatesGroup):
    rate = State()
    text = State()
