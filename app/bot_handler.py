import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import callback_query
from aiogram.utils import executor

from config import create_configuration, admins
import menu as nav
from w_guard.configurator import WGConfigurator

TG_TOKEN = os.environ["TG_TOKEN"]
ANALYTICS_ID = os.environ["CHANNEL_ID"]
SERVER_PUB_KEY = os.environ["SERVER_PUB_KEY"]
SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    name = State()
    pub_key = State()


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    await message.reply("Введите /help для получения списка команд", reply_markup=nav.inline_kb)


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply(
        "Данный бот предоставляет шаблон конфигурации для wireguard\n"
        "/add_user <Name> <Public Key> - Добавить пользователя\n"
        "/del_user <Public Key> - Удалить пользователя\n"
        "/list - Выводит список пользователей"
    )


@dp.message_handler(commands=["add_user"])
async def add_user(msg: types.Message):
    if msg.from_user.username in admins:
        await msg.answer("Введите имя нового пользователя")
        await UserState.name.set()
    else:
        message = f"Permission Denied for {msg.from_user.username}"
        await bot.send_message(msg.from_user.id, message)


@dp.message_handler(state=UserState.name)
async def get_username(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Отлично! Теперь введите публичный ключ.")
    await UserState.next()


@dp.message_handler(state=UserState.pub_key)
async def get_address(msg: types.Message, state: FSMContext):
    await state.update_data(pub_key=msg.text)
    data = await state.get_data()
    wg = WGConfigurator(data["name"], data["pub_key"])
    _ip = wg.update_configuration()
    message = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
    await bot.send_message(msg.from_user.id, message)
    await state.finish()


@dp.message_handler(commands=["del_user"])
async def del_user(msg: types.Message):
    if msg.from_user.username in admins:
        pub_key = msg.get_args()
        wg = WGConfigurator(msg.from_user.username, pub_key)
        message = wg.del_old_peer()
    else:
        message = f"Permission Denied for {msg.from_user.username}"
    await bot.send_message(msg.from_user.id, message)


@dp.callback_query_handler(text=["list"])
async def get_user_list(callback: types.CallbackQuery):
    if callback.from_user.username in admins:
        message = ""
        wg = WGConfigurator(callback.from_user.username)
        peers = wg.get_peers()
        for pub_key, name in peers.items():
            await callback.message.answer(f"{pub_key} : <b>{name}</b>\n", reply_markup=nav.sub_menu, parse_mode="HTML")
        await callback.answer()
    else:
        message = f"Permission Denied for {callback.from_user.username}"
        await callback.message.answer(message, reply_markup=nav.sub_menu)
        await callback.answer()


def start_bot():
    executor.start_polling(dp)


if __name__ == "__main__":
    start_bot()
