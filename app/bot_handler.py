import os
from collections import OrderedDict

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor

import menu as nav
from config import create_configuration, IsAdmin
from states import AddState, DelState
from w_guard.configurator import WGConfigurator
from w_guard.utils import is_pub_key

TG_TOKEN = os.environ["TG_TOKEN"]
ANALYTICS_ID = os.environ["CHANNEL_ID"]
SERVER_PUB_KEY = os.environ["SERVER_PUB_KEY"]
SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]

bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

counter = 0


@dp.message_handler(IsAdmin(), commands=["start"])
async def process_start_command(message: types.Message):
    await message.reply("Введите /help для получения списка команд", reply_markup=nav.inline_kb)


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply(
        "Данный бот предоставляет шаблон конфигурации для wireguard\n"
        "/start - Для вывода меню"
    )


@dp.callback_query_handler(IsAdmin(), text=["main"])
async def main(callback: types.CallbackQuery):
    await callback.message.answer("Выберете действие", reply_markup=nav.inline_kb)
    await callback.answer()


@dp.callback_query_handler(IsAdmin(), text=["add"])
async def add_user(callback: types.CallbackQuery):
    await callback.message.answer("Введите имя нового пользователя")
    await callback.answer()
    await AddState.name.set()


@dp.message_handler(state=AddState.name)
async def get_username(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Теперь введите публичный ключ.")
    await AddState.next()


@dp.message_handler(state=AddState.pub_key)
async def get_user_pub(msg: types.Message, state: FSMContext):
    await state.update_data(pub_key=msg.text)
    data = await state.get_data()
    if is_pub_key(data["pub_key"]):
        _wg = WGConfigurator(data["name"], data["pub_key"])
        _ip = _wg.update_configuration()
        message = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
    else:
        message = "Неверный формат ключа"
    await bot.send_message(msg.from_user.id, message, reply_markup=nav.inline_kb)
    await state.finish()


@dp.callback_query_handler(IsAdmin(), text=["del"])
async def del_user(callback: types.CallbackQuery):
    if callback.message.text == "Выберете действие":
        await callback.message.answer("Введите public key пользователя")
        await callback.answer()
        await DelState.pub_key.set()
    else:
        pub_key = callback.message.text.split()[2]
        _wg = WGConfigurator(callback.message.text.split()[1], pub_key)
        message = _wg.del_old_peer()
        await bot.send_message(callback.from_user.id, message, reply_markup=nav.inline_kb)


@dp.message_handler(state=DelState.pub_key)
async def del_user_pub(msg: types.Message, state: FSMContext):
    await state.update_data(pub_key=msg.text)
    data = await state.get_data()
    _wg = WGConfigurator(msg.from_user.username, data["pub_key"])
    message = _wg.del_old_peer()
    await bot.send_message(msg.from_user.id, message, reply_markup=nav.inline_kb)
    await state.finish()


@dp.callback_query_handler(IsAdmin(), text=["list", "next", "prev"])
async def list_generator(callback: types.CallbackQuery):
    global counter
    wg = WGConfigurator("pit_val")
    peers = OrderedDict(wg.get_peers())
    key_list = sorted(peers.keys())
    if callback.data == "next":
        if counter == len(key_list) - 1:
            counter = 0
        else:
            counter += 1
    elif callback.data == "prev":
        if counter == 0:
            counter = len(key_list) - 1
        else:
            counter -= 1
    message = f"{counter + 1}. <b>{peers[key_list[counter]]}</b>: {key_list[counter]}\n"
    if callback.data == "list":
        await callback.message.answer(message, reply_markup=nav.sub_menu, parse_mode="HTML")
    else:
        await bot.edit_message_text(text=message,
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    reply_markup=nav.sub_menu,
                                    parse_mode="HTML")
    await callback.answer()


def start_bot():
    executor.start_polling(dp)


if __name__ == "__main__":
    start_bot()
