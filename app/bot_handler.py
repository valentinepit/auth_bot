import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import create_configuration
from w_guard.configurator import WGConfigurator

TG_TOKEN = os.environ["TG_TOKEN"]
ANALYTICS_ID = os.environ["CHANNEL_ID"]
SERVER_PUB_KEY = os.environ["SERVER_PUB_KEY"]
SERVER_ADDRESS = os.environ["SERVER_ADDRESS"]

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

discord_channels_path = "discord_bot/discord_channels.json"


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    await message.reply("Введите /help для получения списка команд")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.reply(
        "Данный бот предоставляет шаблон конфигурации для wireguard"
    )


@dp.message_handler(commands=["add_user"])
async def process_add_channel_command(msg: types.Message):
    try:
        pub_key = msg.get_args()
        wg = WGConfigurator(pub_key, msg.from_user.username)
        _ip = wg.update_configuration()
        wg_conf = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
    except (IndexError, ValueError):
        wg_conf = "Параметры должны быть в виде Channel name: Channel id"
    await bot.send_message(msg.from_user.id, wg_conf)


@dp.message_handler(commands=["del_user"])
async def process_add_channel_command(msg: types.Message):
    pub_key = msg.get_args()
    wg = WGConfigurator(pub_key, msg.from_user.username)
    message = wg.del_old_peer()
    await bot.send_message(msg.from_user.id, message)


# @dp.message_handler()
# async def echo_message(msg: types.Message):
#     wg = WGConfigurator(msg.text, msg.from_user.username)
#     _ip = wg.update_configuration()
#     wg_conf = create_configuration(_ip, SERVER_PUB_KEY, SERVER_ADDRESS)
#     await bot.send_message(msg.from_user.id, wg_conf)


def start_bot():
    executor.start_polling(dp)


if __name__ == "__main__":
    start_bot()
