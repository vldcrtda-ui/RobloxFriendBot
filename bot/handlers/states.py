from aiogram.fsm.state import State, StatesGroup


class RegisterState(StatesGroup):
    wait_nick = State()
    wait_age = State()
    wait_language = State()
    wait_games = State()
    wait_bio = State()
    wait_photo = State()
