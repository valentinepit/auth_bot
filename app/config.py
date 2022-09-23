import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

dsn = "https://cd6ebdfaf653491fadbac391ccf8d201@sentry.dexpa.io/26"

sentry_sdk.init(
    dsn=dsn,
    integrations=[sentry_logging],
    debug=False,
)

logging.basicConfig(format="%(asctime)s -%(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


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
