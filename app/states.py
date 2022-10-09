from aiogram.dispatcher.filters.state import State, StatesGroup


class AddState(StatesGroup):
    name = State()
    pub_key = State()


class DelState(StatesGroup):
    pub_key = State()
