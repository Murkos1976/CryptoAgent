import os
import time
import base64
import hashlib
import hmac
import urllib.parse
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))

KRAKEN_API_KEY = os.environ.get("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.environ.get("KRAKEN_API_SECRET")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

KRAKEN_URL = "https://api.kraken.com"
KRAKEN_PATH = "/0/private/AddOrder"


def send_approval_request():
    message = (
        "CryptoAgent Trade Test\n\n"
        "SOL - BUY\n"
        "Amount: C$25\n\n"
        "Approve Kraken validation?"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ APPROVE",
                    "callback_data": "KRAKEN_APPROVE"
                },
                {
                    "text": "❌ REJECT",
                    "callback_data": "KRAKEN_REJECT"
                }
            ]
        ]
    }

    response = requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "reply_markup": keyboard
        },
        timeout=20
    )

    response.raise_for_status()
    print("Approval request sent to Telegram.")


def kraken_validation_test():
    nonce = str(int(time.time() * 1000))

    data = {
        "nonce": nonce,
        "ordertype": "market",
        "type": "buy",
        "volume": "0.1",
        "pair": "SOLCAD",
        "validate": "true"
    }

    postdata = urllib.parse.urlencode(data)

    message = KRAKEN_PATH.encode() + hashlib.sha256(
        (nonce + postdata).encode()
    ).digest()
