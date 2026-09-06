import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

CHECK_EVERY_SECONDS = 300  # 5 minutes

# Price levels in CAD
SOL_BUY = 125.00
SOL_SELL = 150.00

XRP_BUY = 1.30
XRP_SELL = 2.00

last_sol_zone = None
last_xrp_zone = None
telegram_offset = None


def get_price(pair):
    response = requests.get(
        f"https://api.kraken.com/0/public/Ticker?pair={pair}",
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise Exception(data["error"])

    key = list(data["result"].keys())[0]

    return float(data["result"][key]["c"][0])


def send_message(text, keyboard=None):
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

    digits = 2 if symbol == "SOL" else 4

    message = (
        f"🚨 {symbol} {action} ALERT\n\n"
        f"1 {symbol} = C${price:.{digits}f} CAD\n"
        f"Suggested amount: C$50\n\n"
        f"Approve or reject this trade idea."
    )

    send_message(message, keyboard)


def check_callbacks():
    global telegram_offset

    params = {
        "timeout": 1
    }

    if telegram_offset is not None:
        params["offset"] = telegram_offset

    response = requests.get(
        f"{TG_URL}/getUpdates",
        params=params,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    for update in data.get("result", []):
        telegram_offset = update["update_id"] + 1

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


def sol_zone(price):
    if price <= SOL_BUY:
        return "BUY"

    if price >= SOL_SELL:
        return "SELL"

    return "NORMAL"


def xrp_zone(price):
    if price <= XRP_BUY:
        return "BUY"

    if price >= XRP_SELL:
        return "SELL"

    return "NORMAL"


print("CryptoAgent started.")
print("Prices are in CAD.")
print("Checking every 5 minutes.")


while True:
    try:
        sol_price = get_price("SOLCAD")
        xrp_price = get_price("XRPCAD")

        price_message = (
            "📊 CRYPTO PRICE UPDATE\n\n"
            f"1 SOL = C${sol_price:.2f} CAD\n"
            f"1 XRP = C${xrp_price:.4f} CAD\n\n"
            "Next check in 5 minutes."
        )

        print(price_message)
        send_message(price_message)

        current_sol_zone = sol_zone(sol_price)
        current_xrp_zone = xrp_zone(xrp_price)

        if current_sol_zone != last_sol_zone:
            if current_sol_zone == "BUY":
                send_trade_alert("SOL", "BUY", sol_price)

            elif current_sol_zone == "SELL":
                send_trade_alert("SOL", "SELL", sol_price)

            last_sol_zone = current_sol_zone

        if current_xrp_zone != last_xrp_zone:
            if current_xrp_zone == "BUY":
                send_trade_alert("XRP", "BUY", xrp_price)

            elif current_xrp_zone == "SELL":
                send_trade_alert("XRP", "SELL", xrp_price)

            last_xrp_zone = current_xrp_zone

        check_callbacks()

    except Exception as e:
        print("Monitor error:", e)

    print("Next check in 5 minutes...")
    time.sleep(CHECK_EVERY_SECONDS)
