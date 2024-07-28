from src.states.states_authorization import StatesAuthorization, registration_container
from src.states.states_menu import StatesMain
from src.database import db

from aiogram import Router
from aiogram.types import Message
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

router: Router = Router()

dbc = db.DataBaseConnection(host="localhost", port='port', user="postgres", password="password", database="TelegramBotShoppingBase")

@router.message(StatesAuthorization.state_password_up)
async def password_up(message: Message, state: FSMContext) -> None:
    if len(message.text) >= 8 and any(i.isdigit() for i in message.text) and any(i.isalpha() for i in message.text):
        registration_container['password'] = message.text

        await dbc.connection()
        await dbc.transaction_insert_registration(
            login=registration_container['login'],
            password=registration_container['password'],
            user_id=message.from_user.id)
        await dbc.close()

        store_button = KeyboardButton(text='Магазин')
        profile_button = KeyboardButton(text='Профиль')
        location_button = KeyboardButton(text='Подтвердить геолокацию', request_location=True)
        contact_button = KeyboardButton(text='Подтвердить номер телефона', request_contact=True)

        reply_keybord_builder = ReplyKeyboardBuilder()
        reply_keybord_builder.row(store_button, profile_button)
        reply_keybord_builder.row(location_button, contact_button)

        km = reply_keybord_builder.as_markup(resize_keyboard=True)

        await state.set_state(StatesMain.state_main_menu)

        await message.answer('Вы зарегистрированы', reply_markup=km)
    else:
        await message.answer('этот пароль не подходит, повторите попытку.')


@router.message(StatesAuthorization.state_password_in)
async def password_in(message: Message, state: FSMContext) -> None:
    await dbc.connection()
    password = await dbc.query_select_password(message.from_user.id)
    await dbc.close()
    if len(message.text) >= 8 and any(i.isdigit() for i in message.text) and any(i.isalpha() for i in message.text):
        if message.text == password[0][0]:
            await state.set_state(StatesMain.state_main_menu)

            store_button = KeyboardButton(text='Меню')
            reply_keybord_builder = ReplyKeyboardBuilder()
            reply_keybord_builder.add(store_button)
            km = reply_keybord_builder.as_markup(resize_keyboard=True)

            await message.answer('Вы вошли', reply_markup=km)
        else:
            await message.answer('неправильный пароль, повторите попытку.')
    else:
        await message.answer('некорректный пароль, повторите попытку.')


@router.message(StatesMain.state_main_menu)
async def menu(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    store_button = KeyboardButton(text='Магазин')
    profile_button = KeyboardButton(text='Профиль')

    reply_keybord_builder = ReplyKeyboardBuilder()

    reply_keybord_builder.row(store_button, profile_button)

    await dbc.connection()
    user_location = await dbc.query_select_location(message.from_user.id)
    user_phone = await dbc.query_select_phone(message.from_user.id)
    await dbc.close()

    try:
        if user_location[0][0] is None:
            location_button = KeyboardButton(text='Подтвердить геолокацию', request_location=True)
            reply_keybord_builder.row(location_button)

        if user_phone[0][0] is None:
            contact_button = KeyboardButton(text='Подтвердить номер телефона', request_contact=True)
            reply_keybord_builder.add(contact_button)
    except:
        pass

    km = reply_keybord_builder.as_markup(resize_keyboard=True,
                                         one_time_keyboard=False)

    await message.answer(text='Главное меню:', reply_markup=km)


@router.message(F.text.lower() == 'меню')
async def go_to_menu(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None and current_state not in StatesAuthorization:
        await menu(message, state)