import os

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext

from aiogram.utils import executor

from config import create_configuration, admins
import menu as nav
from states import AddState, DelState
from w_guard.configurator import WGConfigurator

TG_TOKEN = os.environ["TG_TOKEN"]
ANALYTICS_ID = os.environ["CHANNEL_ID"]
SERVER_PUB_KEY = os.environ["SERVER_PUB_KEY"]
SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    await message.reply("Введите /help для получения списка команд", reply_markup=nav.inline_kb)


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply(
        "Данный бот предоставляет шаблон конфигурации для wireguard\n"
        "/start - Для вывода меню"
    )


@dp.callback_query_handler(text=["add"])
async def add_user(callback: types.CallbackQuery):
    if callback.from_user.username in admins:
        await callback.message.answer("Введите имя нового пользователя")
        await callback.answer()
        await AddState.name.set()
    else:
        message = f"Permission Denied for {callback.from_user.username}"
        await bot.send_message(callback.from_user.id, message)


@dp.message_handler(state=AddState.name)
async def get_username(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Отлично! Теперь введите публичный ключ.")
    await AddState.next()


@dp.message_handler(state=AddState.pub_key)
async def get_new_user_pub(msg: types.Message, state: FSMContext):
    await state.update_data(pub_key=msg.text)
    data = await state.get_data()
    wg = WGConfigurator(data["name"], data["pub_key"])
    _ip = wg.update_configuration()
    message = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
    await bot.send_message(msg.from_user.id, message, reply_markup=nav.inline_kb)
    await state.finish()


@dp.callback_query_handler(text=["del"])
async def del_user(callback: types.CallbackQuery):
    if callback.from_user.username in admins:
        await callback.message.answer("Введите public key пользователя")
        await callback.answer()
        await DelState.pub_key.set()
    else:
        message = f"Permission Denied for {callback.from_user.username}"
        await bot.send_message(callback.from_user.id, message)


@dp.message_handler(state=DelState.pub_key)
async def get_old_user_pub(msg: types.Message, state: FSMContext):
    await state.update_data(pub_key=msg.text)
    data = await state.get_data()
    wg = WGConfigurator(msg.from_user.username, data["pub_key"])
    message = wg.del_old_peer()
    await bot.send_message(msg.from_user.id, message, reply_markup=nav.inline_kb)
    await state.finish()


@dp.callback_query_handler(text=["list"])
async def get_user_list(callback: types.CallbackQuery):
    if callback.from_user.username in admins:
        wg = WGConfigurator(callback.from_user.username)
        peers = wg.get_peers()
        for pub_key, name in peers.items():
            await callback.message.answer(f"{pub_key} : <b>{name}</b>\n", parse_mode="HTML")
        await callback.answer()
    else:
        message = f"Permission Denied for {callback.from_user.username}"
        await callback.message.answer(message, reply_markup=nav.sub_menu)
        await callback.answer()


def start_bot():
    executor.start_polling(dp)


if __name__ == "__main__":
    start_bot()
