import os
import time
import requests
from datetime import datetime

# =========================
# TELEGRAM SETTINGS
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")

if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID is missing")


# =========================
# SETTINGS
# =========================

CHECK_INTERVAL = 300  # 5 minutes

COINS = {
    "SOL": "SOLCAD",
    "XRP": "XRPCAD",
    "ETH": "ETHCAD",
}


# =========================
# GET PRICE FROM KRAKEN
# =========================

def get_kraken_price(pair):
    url = "https://api.kraken.com/0/public/Ticker"

    try:
        response = requests.get(
            url,
            params={"pair": pair},
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            print(f"Kraken error for {pair}: {data['error']}")
            return None

        result = data.get("result", {})

        if not result:
            print(f"No Kraken result for {pair}")
            return None

        ticker = next(iter(result.values()))

        return float(ticker["c"][0])

    except Exception as e:
        print(f"Error getting {pair}: {e}")
        return None


# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        response.raise_for_status()

        print("Telegram message sent successfully.")

    except Exception as e:
        print(f"Telegram error: {e}")


# =========================
# BUILD PRICE MESSAGE
# =========================

def build_price_message():

    prices = {}

    for symbol, pair in COINS.items():
        prices[symbol] = get_kraken_price(pair)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = "💰 Crypto Prices (CAD)\n\n"

    if prices["SOL"] is not None:
        message += f"◎ SOL: ${prices['SOL']:,.2f} CAD\n"
    else:
        message += "◎ SOL: unavailable\n"

    if prices["XRP"] is not None:
        message += f"✕ XRP: ${prices['XRP']:,.4f} CAD\n"
    else:
        message += "✕ XRP: unavailable\n"

    if prices["ETH"] is not None:
        message += f"◆ ETH: ${prices['ETH']:,.2f} CAD\n"
    else:
        message += "◆ ETH: unavailable\n"

    message += f"\n🕒 {now}"

    return message


# =========================
# MAIN LOOP
# =========================

def main():

    print("CryptoAgent started.")
    print("Sending prices every 5 minutes.")

    while True:

        try:
            message = build_price_message()

            print(message)

            send_telegram(message)

        except Exception as e:
            print(f"Main loop error: {e}")

        print("Waiting 5 minutes...")
        time.sleep(CHECK_INTERVAL)


# =========================
# START
# =========================

main()
