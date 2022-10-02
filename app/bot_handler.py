import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import create_configuration, admins
from w_guard.configurator import WGConfigurator

TG_TOKEN = os.environ["TG_TOKEN"]
ANALYTICS_ID = os.environ["CHANNEL_ID"]
SERVER_PUB_KEY = os.environ["SERVER_PUB_KEY"]
SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    await message.reply("Введите /help для получения списка команд")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply(
        "Данный бот предоставляет шаблон конфигурации для wireguard\n"
        "/add_user <Public Key> - Добавить пользователя\n"
        "/del_user <Public Key> - Удалить пользователя\n"
        "/list - Выводит список пользователей"
    )


@dp.message_handler(commands=["add_user"])
async def process_add_channel_command(msg: types.Message):
    if msg.from_user.username in admins:
        pub_key = msg.get_args()
        wg = WGConfigurator(msg.from_user.username, pub_key)
        _ip = wg.update_configuration()
        wg_conf = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
    else:
        wg_conf = f"Permission Denied for {msg.from_user.username}"
    await bot.send_message(msg.from_user.id, wg_conf)


@dp.message_handler(commands=["del_user"])
async def process_add_channel_command(msg: types.Message):
    if msg.from_user.username in admins:
        pub_key = msg.get_args()
        wg = WGConfigurator(msg.from_user.username, pub_key)
        message = wg.del_old_peer()
    else:
        message = f"Permission Denied for {msg.from_user.username}"
    await bot.send_message(msg.from_user.id, message)


@dp.message_handler(commands=["list"])
async def process_add_channel_command(msg: types.Message):
    message = ""
    wg = WGConfigurator(msg.from_user.username)
    peers = wg.get_peers()
    for pub_key, name in peers.items():
        message += f"{pub_key} : {name}\n"
    await bot.send_message(msg.from_user.id, message)


def start_bot():
    executor.start_polling(dp)


if __name__ == "__main__":
    start_bot()
