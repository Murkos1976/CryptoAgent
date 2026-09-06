import os
import time
import base64
import hashlib
import hmac
import urllib.parse
import requests

BOT = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
KEY = os.environ["KRAKEN_API_KEY"]
SECRET = os.environ["KRAKEN_API_SECRET"]

TG = f"https://api.telegram.org/bot{BOT}"
PATH = "/0/private/AddOrder"


def send_request():
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ APPROVE", "callback_data": "YES"},
            {"text": "❌ REJECT", "callback_data": "NO"}
        ]]
    }

    requests.post(
        f"{TG}/sendMessage",
        json={
            "chat_id": CHAT,
            "text": "Kraken TEST\nBUY 0.1 SOL\nVALIDATION ONLY - NO REAL TRADE",
            "reply_markup": keyboard
        },
        timeout=20
    ).raise_for_status()

    print("Approval request sent to Telegram.")


def validate_kraken():
    nonce = str(int(time.time() * 1000))

    data = {
        "nonce": nonce,
        "pair": "SOLCAD",
        "type": "buy",
        "ordertype": "market",
        "volume": "0.1",
        "validate": "true"
    }

    post = urllib.parse.urlencode(data)

    sha = hashlib.sha256(
        (nonce + post).encode()
    ).digest()

    message = PATH.encode() + sha

    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(SECRET),
            message,
            hashlib.sha512
        ).digest()
    ).decode()

    response = requests.post(
        "https://api.kraken.com" + PATH,
        headers={
            "API-Key": KEY,
            "API-Sign": signature
        },
        data=data,
        timeout=20
    )

    result = response.json()

    print("Kraken response:", result)

    if result.get("error"):
        print("VALIDATION ERROR:", result["error"])
    else:
        print("KRAKEN VALIDATION OK")
        print("NO REAL TRADE EXECUTED")


def wait():
    print("Waiting for APPROVE or REJECT...")

    offset = None

    while True:
        params = {"timeout": 20}

        if offset:
            params["offset"] = offset

        result = requests.get(
            f"{TG}/getUpdates",
            params=params,
            timeout=30
        ).json()

        for update in result.get("result", []):
            offset = update["update_id"] + 1

            callback = update.get("callback_query")

            if not callback:
                continue

            if str(callback["message"]["chat"]["id"]) != str(CHAT):
                continue

            requests.post(
                f"{TG}/answerCallbackQuery",
                json={"callback_query_id": callback["id"]},
                timeout=20
            )

            if callback.get("data") == "YES":
                print("APPROVED")
                validate_kraken()
                return

            if callback.get("data") == "NO":
                print("REJECTED")
                print("NO TRADE EXECUTED")
                return


send_request()
wait()
