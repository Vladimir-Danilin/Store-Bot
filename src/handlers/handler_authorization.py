from src.states.states_authorization import StatesAuthorization, registration_container
from src.database import db

from aiogram import Router
from aiogram.types import Message
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

router: Router = Router()

dbc = db.DataBaseConnection(host="localhost", port='port', user="postgres", password="password", database="TelegramBotShoppingBase")

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(StatesAuthorization.state_start)

    sing_up_button = KeyboardButton(text='Зарегистрироваться')
    sing_in_button = KeyboardButton(text='Войти')

    reply_keybord_builder = ReplyKeyboardBuilder()
    reply_keybord_builder.add(sing_up_button)
    reply_keybord_builder.add(sing_in_button)

    km = reply_keybord_builder.as_markup(resize_keyboard=True,
                                         input_field_placeholder="Выберите способ авторизация.",
                                         one_time_keyboard=True)
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}!\nЧтобы начать использовать бота авторизуйтесь по одной из кнопок в низу чата.",
        reply_markup=km)


@router.message(F.text.lower() == "зарегистрироваться")
async def sing_up(message: Message, state: FSMContext) -> None:
    sing_in_button = KeyboardButton(text='Войти')

    reply_keybord_builder = ReplyKeyboardBuilder()
    reply_keybord_builder.add(sing_in_button)

    km = reply_keybord_builder.as_markup(resize_keyboard=True,
                                         one_time_keyboard=True)
    await message.answer("""Введите ФИО или оставте отправте !, если ваше ФИО используется как логин телеграмма.
Эти ФИО будет вписанны в ФИО при отправке посылки""",
                         reply_markup=km)
    await state.set_state(StatesAuthorization.state_login_up)


@router.message(F.text.lower() == "войти")
async def sing_in(message: Message, state: FSMContext) -> None:
    sing_up_button = KeyboardButton(text='Зарегистрироваться')

    reply_keybord_builder = ReplyKeyboardBuilder()
    reply_keybord_builder.add(sing_up_button)

    km = reply_keybord_builder.as_markup(resize_keyboard=True,
                                         one_time_keyboard=True)
    await message.answer(
        "Введите своё ФИО или отправте !, если ваш телеграмм логин совпадает с вашим ФИО в нашем магазине.",
        reply_markup=km)

    await state.set_state(StatesAuthorization.state_login_in)


@router.message(StatesAuthorization.state_login_up)
async def login_up(message: Message, state: FSMContext) -> None:
    await dbc.connection()
    login = await dbc.query_select_login(message.from_user.id)
    user_id = await dbc.query_select_user_id(message.from_user.id)
    await dbc.close()
    
    login = '!' if len(login) == 0 else message.from_user.id
    user_id = '!' if len(user_id) == 0 else message.from_user.id

    input_login = message.text if message.text != '!' else message.from_user.full_name

    if user_id[0][0] != message.from_user.id:
        if login[0][0] != input_login:
            registration_container['login'] = input_login
            await message.answer("""Отлично теперь введите пароль, он должен содержать
хотя бы одну букву и одну цифру, а так же длина пороля
должна быть не меньше 8 символов.""")

            await state.set_state(StatesAuthorization.state_password_up)
        else:
            await message.answer('Такой логин уже существует, введите другой.')
    else:
        await message.answer('На этом аккаунте уже была произведенна регистрация')


@router.message(StatesAuthorization.state_login_in)
async def login_in(message: Message, state: FSMContext) -> None:
    await dbc.connection()
    login = await dbc.query_select_login(message.from_user.id)
    await dbc.close()

    if login[0][0] == message.text:
        await message.answer('Отлично теперь введите пароль.')

        await state.set_state(StatesAuthorization.state_password_in)
    elif login[0][0] == message.from_user.full_name and '!' in message.text:
        await message.answer('Отлично теперь введите пароль.')

        await state.set_state(StatesAuthorization.state_password_in)
    else:
        await message.answer('Такого логина не существует.')