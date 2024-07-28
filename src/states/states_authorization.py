from aiogram.fsm.state import StatesGroup, State

registration_container = {'login': '', 'password': ''}

class StatesAuthorization(StatesGroup):
    state_start = State()
    state_login_in = State()
    state_login_up = State()
    state_password_up = State()
    state_password_in = State()
