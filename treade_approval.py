import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_test_trade():
    message = (
        "🧪 CryptoAgent Trade Approval Test\n\n"
        "SOL — BUY\n"
        "Amount: C$25.00\n\n"
        "TEST ONLY — NO TRADE WILL BE EXECUTED"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ APPROVE",
                    "callback_data": "TEST_APPROVE"
                },
                {
                    "text": "❌ REJECT",
                    "callback_data": "TEST_REJECT"
                }
            ]
        ]
    }

    response = requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "reply_markup": keyboard
        },
        timeout=20
    )

    response.raise_for_status()
    print("Approval request sent to Telegram.")


def wait_for_response():
    offset = None
    print("Waiting for APPROVE or REJECT...")

    while True:
        params = {
            "timeout": 20
        }

        if offset is not None:
            params["offset"] = offset

        response = requests.get(
            f"{BASE_URL}/getUpdates",
            params=params,
            timeout=30
        )

        data = response.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            callback = update.get("callback_query")

            if not callback:
                continue

            callback_chat_id = str(
                callback["message"]["chat"]["id"]
            )

            if callback_chat_id != CHAT_ID:
                continue

            choice = callback.get("data")

            requests.post(
                f"{BASE_URL}/answerCallbackQuery",
                json={
                    "callback_query_id": callback["id"]
                },
                timeout=20
            )

            if choice == "TEST_APPROVE":
                print("APPROVED")
                print("TEST ONLY - NO TRADE EXECUTED")
