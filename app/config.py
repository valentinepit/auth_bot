import logging

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types.message import Message

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

dsn = os.environ["DSN"]

sentry_sdk.init(
    dsn=dsn,
    integrations=[sentry_logging],
    debug=False,
)

logging.basicConfig(format="%(asctime)s -%(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ADMINS = []


class IsAdmin(BoundFilter):
    async def check(self, msg: Message):
        user = msg.from_user.id
        if user not in ADMINS:
            await msg.answer('Только для администраторов')
        return user in ADMINS


def create_configuration(_ip, pub_key, server_ip):
    return f"[Interface]\nPrivateKey = <Your key>\n" \
           f"ListenPort = 63665\n" \
           f"Address = {_ip}\n" \
           f"DNS = 1.1.1.1\n" \
           f"MTU = 1380\n\n" \
           f"[Peer]\n" \
           f"PublicKey = {pub_key}\n" \
           f"AllowedIPs = 0.0.0.0/0 # 10.30.0.0/20, 10.1.9.0/24, 10.10.128.3/32\n" \
           f"Endpoint = {server_ip}\n" \
           f"PersistentKeepalive = 15"
