from config import TOKEN, OWN_IDS
from src.database import db
from src.handlers import handler_authorization
from src.handlers import handler_menu
from src.handlers import handler_shop

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message


dp = Dispatcher()

dp.include_router(handler_authorization.router)
dp.include_router(handler_menu.router)
dp.include_router(handler_shop.router)

dbc = db.DataBaseConnection(host="localhost", port='port', user="postgres", password="password", database="TelegramBotShoppingBase")

@dp.message(Command('reset'))
async def reset(message: Message):
    if message.from_user.id in OWN_IDS:
        await dbc.connection()
        await dbc.reset_user(message.from_user.id)
        await dbc.close()


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
