[12:51 AM, 9/6/2026] Murkos: import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHECK_EVERY_SECONDS = 180  # 3 minutes

# Alert levels in USD
SOL_BUY = 120.00
SOL_SELL = 140.00

XRP_BUY = 1.35
XRP_SELL = 1.55


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram settings are missing.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=20
        )

        response.raise_for_status()
        print("Telegram message sent.")

    except Exception as e:
        print("Telegram error:", e)


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


print("CryptoAgent started.")
print("Prices are in USD.")
print("Checking every 3 minutes.")


while True:
    try:
        sol_price = get_price("SOLUSD")
        xrp_price = get_price("XRPUSD")

        message = (
            "📊 CRYPTO PRICE UPDATE\n\n"
            f"SOL\n"
            f"1 SOL = ${sol_price:.2f} USD\n"
        )

        if sol_price <= SOL_BUY:
            message += "🟢 BUY LEVEL\n"
        elif sol_price >= SOL_SELL:
            message += "🔴 SELL LEVEL\n"
        else:
            message += "⚪ WAIT\n"

        message += (
            "\n"
            f"XRP\n"
            f"1 XRP = ${xrp_price:.4f} USD\n"
        )

        if xrp_price <= XRP_BUY:
            message += "🟢 BUY LEVEL\n"
        elif xrp_price >= XRP_SELL:
            message += "🔴 SELL LEVEL\n"
        else:
[12:56 AM, 9/6/2026] Murkos: import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID"))

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

CHECK_EVERY_SECONDS = 180  # 3 minutes

# Price levels in USD
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


def send_price_update(sol_price, xrp_price):
    message = (
        "📊 CryptoAgent Price Update\n\n"
        f"1 SOL = ${sol_price:.2f} USD\n"
        f"1 XRP = ${xrp_price:.4f} USD\n\n"
        "Next check in 3 minutes."
    )

    requests.post(
        f"{TG_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    ).raise_for_status()


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

    message = (
        f"🚨 {symbol} {action} ALERT\n\n"
        f"Price: ${price:.4f} USD\n"
        f"Suggested amount: C$50\n\n"
        f"Do you approve this trade idea?"
    )

    requests.post(
        f"{TG_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "reply_markup": keyboard
        },
        timeout=20
    ).raise_for_status()

    print(f"{symbol} {action} approval request sent.")


def check_callbacks():
    response = requests.get(
        f"{TG_URL}/getUpdates",
        params={"timeout": 1},
        timeout=10
    )

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
            print("TRADE IDEA APPROVED:", choice)

        elif choice.startswith("REJECT_"):
            print("TRADE IDEA REJECTED:", choice)


print("CryptoAgent started.")
print("Prices are in USD.")
print("Checking every 3 minutes.")


while True:
    try:
        sol_price = get_price("SOLUSD")
        xrp_price = get_price("XRPUSD")

        print(f"SOL: ${sol_price:.2f} USD")
        print(f"XRP: ${xrp_price:.4f} USD")

        send_price_update(sol_price, xrp_price)

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

    print("Next check in 3 minutes...")
    time.sleep(CHECK_EVERY_SECONDS)
