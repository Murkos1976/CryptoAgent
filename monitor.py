import os
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHECK_EVERY_SECONDS = 300  # 5 minutes

# Alert rules in USD
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
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=20
        ).raise_for_status()

        print("Telegram alert sent.")

    except Exception as e:
        print("Telegram error:", e)


def get_kraken_price(pair):
    url = f"https://api.kraken.com/0/public/Ticker?pair={pair}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    if data.get("error"):
        raise Exception(data["error"])

    result = data["result"]
    key = list(result.keys())[0]

    return float(result[key]["c"][0])


def check_sol():
    price = get_kraken_price("SOLUSD")

    print(f"SOL: ${price:.2f} USD")

    if price <= SOL_BUY:
        send_telegram(
            f"🟢 SOL BUY ALERT\n\n"
            f"Price: ${price:.2f} USD\n"
            f"Buy level: ${SOL_BUY:.2f}\n"
            f"Suggested amount: C$50\n\n"
            f"Open Kraken to place the trade."
        )

    elif price >= SOL_SELL:
        send_telegram(
            f"🔴 SOL SELL ALERT\n\n"
            f"Price: ${price:.2f} USD\n"
            f"Sell level: ${SOL_SELL:.2f}\n\n"
            f"Open Kraken to place the trade."
        )


def check_x
