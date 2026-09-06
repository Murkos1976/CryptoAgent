import os
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
