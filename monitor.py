import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

CHECK_EVERY_SECONDS = 180

SOL_BUY = 120.00
SOL_SELL = 140.00

XRP_BUY = 1.35
XRP_SELL = 1.55


def get_price(pair):
    url = f"https://api.kraken.com/0/public/Ticker?pair={pair}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    if data.get("error"):
        raise Exception(data["error"])

    result = data["result"]
    key = list(result.keys())[0]

    return float(result[key]["c"][0])


def send_message(text, keyboard=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram settings are missing.")
        return

    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    if keyboard is not None:
        payload["reply_markup"] = keyboard

    response = requests.post(
        f"{TG_URL}/sendMessage",
        json=payload,
        timeout=20
    )

    response.raise_for_status()


def send_trade_alert(symbol, action, price):
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ APPROVE",
                    "callback_data": f"APPROVE_{symbol}_{action}"
                },
                {
                    "text": "❌ REJECT",
                    "callback_data": f"REJECT_{symbol}_{action}"
                }
            ]
        ]
    }

    price_format = f"{price:.2f}" if symbol == "SOL" else f"{price:.4f}"

    message = (
        f"🚨 {symbol} {action} ALERT\n\n"
        f"1 {symbol} = ${price_format} USD\n"
        f"Suggested amount: C$50\n\n"
        f"Approve or reject this trade idea."
    )

    send_message(message, keyboard)
    print(f"{symbol} {action} alert sent.")


def check_callbacks():
    try:
        response = requests.get(
            f"{TG_URL}/getUpdates",
            params={"timeout": 1},
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        for update in data.get("result", []):
            callback = update.get("callback_query")

            if not callback:
                continue

            callback_chat_id = str(
                callback["message"]["chat"]["id"]
            )

            if callback_chat_id != CHAT_ID:
                continue

            choice = callback.get("data", "")

            requests.post(
                f"{TG_URL}/answerCallbackQuery",
                json={
                    "callback_query_id": callback["id"]
                },
                timeout=10
            )

            if choice.startswith("APPROVE_"):
                send_message(
                    "✅ APPROVED\n\n"
                    "Trade idea confirmed.\n"
                    "Open Kraken or Robinhood to execute manually."
                )

            elif choice.startswith("REJECT_"):
                send_message(
                    "❌ REJECTED\n\n"
                    "No trade."
                )

    except Exception as e:
        print("Callback error:", e)


print("CryptoAgent started.")
print("Prices are in USD.")
print("Checking every 3 minutes.")


while True:
    try:
        sol_price = get_price("SOLUSD")
        xrp_price = get_price("XRPUSD")

        price_message = (
            "📊 CRYPTO PRICE UPDATE\n\n"
            f"1 SOL = ${sol_price:.2f} USD\n"
            f"1 XRP = ${xrp_price:.4f} USD\n\n"
            "Next check in 3 minutes."
        )

        print(price_message)
        send_message(price_message)

        if sol_price <= SOL_BUY:
            send_trade_alert("SOL", "BUY", sol_price)

        elif sol_price >= SOL_SELL:
            send_trade_alert("SOL", "SELL", sol_price)

        if xrp_price <= XRP_BUY:
            send_trade_alert("XRP", "BUY", xrp_price)

        elif xrp_price >= XRP_SELL:
            send_trade_alert("XRP", "SELL", xrp_price)

        check_callbacks()

    except Exception as e:
        print("Monitor error:", e)
