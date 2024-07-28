from aiogram.fsm.state import StatesGroup, State


class StatesMain(StatesGroup):
    state_main_menu = State()
    state_shop = State()
    state_selected_type = State()
    state_selected_category = State()
    state_buy_product = State()
