from src.states.states_menu import StatesMain
from handler_menu import menu
from src.database import db

from geopy.geocoders import Nominatim

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hunderline
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton, InlineKeyboardBuilder, InlineKeyboardButton

router: Router = Router()

dbc = db.DataBaseConnection(host="localhost", port='port', user="postgres", password="password", database="TelegramBotShoppingBase")

@router.message(F.text.lower() == 'магазин')
async def shop(message: Message, state: FSMContext):
    await state.set_state(StatesMain.state_selected_type)
    await dbc.connection()
    types_products = await dbc.query_select_types()
    await dbc.close()

    inline_keybord_builder = InlineKeyboardBuilder()
    types_products = set(types_products)
    for i in types_products:
        inline_keybord_builder.row(InlineKeyboardButton(text=i[0], callback_data=i[0]))

    ikm = inline_keybord_builder.as_markup(resize_keyboard=True)

    main_menu_button = KeyboardButton(text='Меню')
    reply_keybord_builder = ReplyKeyboardBuilder()
    reply_keybord_builder.row(main_menu_button)

    km = reply_keybord_builder.as_markup(resize_keyboard=True,
                                         one_time_keyboard=True)

    await state.set_state(StatesMain.state_selected_type)
    await message.answer('Магазин', reply_markup=km)
    await message.answer('Выберите категорию:', reply_markup=ikm)


@router.callback_query(StatesMain.state_selected_type or 'back_to_type')
async def selected_type(callback: CallbackQuery, state: FSMContext):
    await dbc.connection()
    categories = await dbc.query_select_categories_by_type(type_product=callback.data)
    await dbc.close()
    inline_keybord_builder = InlineKeyboardBuilder()

    for j in set(categories):
        inline_keybord_builder.row(InlineKeyboardButton(text=j[0], callback_data=j[0]))

    km = inline_keybord_builder.as_markup(resize_keyboard=True)

    await state.set_state(StatesMain.state_selected_category)
    await callback.message.answer('Выберите тип товара', reply_markup=km)


@router.callback_query(StatesMain.state_selected_category)
async def selected_category(callback: CallbackQuery, state: FSMContext):
    await dbc.connection()
    products = await dbc.query_select_products_by_category(category=callback.data)
    await dbc.close()

    for i in products:
        inline_keybord_builder = InlineKeyboardBuilder()
        inline_keybord_builder.row(InlineKeyboardButton(text='Купить', callback_data=i[5]))
        km = inline_keybord_builder.as_markup(resize_keyboard=True)

        await callback.message.answer_photo(photo=i[3])
        if int(i[2]) > 0:
            await callback.message.answer(f"""Название: {i[0]}
Цена: {hunderline(int(i[1]) - (i[1] / 100 * i[2]))}
скидка: {i[2]}%
Описание:
{i[4]}""", reply_markup=km)
        else:
            await callback.message.answer(f"""Название: {i[0]}
Цена: {int(i[1])}
Описание:
{i[4]}""", reply_markup=km)

    await state.set_state(StatesMain.state_buy_product)
    await callback.message.answer(f'товаров отображенно {len(products)}')


@router.callback_query(StatesMain.state_buy_product)
async def buy_product(callback: CallbackQuery, state: FSMContext):
    var = callback.data


@router.message(F.text.lower() == 'профиль')
async def profile(message: Message):
    await dbc.connection()
    user_info = await dbc.query_select_user_info(message.from_user.id)
    await dbc.close()
    user_info = user_info[0]
    if user_info[3] is not None:
        addres = await find_location(user_info[3][0], user_info[3][1])
    else:
        addres = 'не привязан'

    await message.answer(f"""Пользователь {user_info[0]}
Баланс: {user_info[1]}
Номер телефона: {'не привязан' if user_info[2] is None else user_info[2]}
Адрес: {addres}""")


@router.message(F.contact)
async def update_phone_number(message: Message, state: FSMContext) -> None:
    await dbc.connection()
    user_phone = await dbc.query_select_phone(message.from_user.id)
    if user_phone[0][0] is None:
        await dbc.transaction_update_phone_number(phone_number=message.contact.phone_number,
                                                  user_id=message.from_user.id)
        await dbc.close()
        await message.answer('Ваш номер телефона привязан к аккаунту.')

        await menu(message, state)
    else:
        await menu(message, state)


@router.message(F.location)
async def update_location(message: Message, state: FSMContext) -> None:
    await dbc.connection()
    user_location = await dbc.query_select_location(message.from_user.id)
    if user_location[0][0] is None:
        await dbc.transaction_update_location(location=[message.location.latitude, message.location.longitude],
                                              user_id=message.from_user.id)
        await dbc.close()
        await message.answer('Ваше местоположение привязанно к аккаунту.')

        await menu(message, state)
    else:
        await menu(message, state)


async def find_location(latitude: str, longitude: str):
    geolocator = Nominatim(user_agent='exaple')
    location = geolocator.geocode(str(latitude) + "," + str(longitude))
    return location[0]