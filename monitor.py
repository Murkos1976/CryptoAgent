import os
import time
import requests


# =========================================================
# SETTINGS
# =========================================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Check prices every 5 minutes
CHECK_EVERY_SECONDS = 300

# Alert levels in CAD
SOL_BUY = 125.00
SOL_SELL = 150.00

XRP_BUY = 1.30
XRP_SELL = 2.00


# Keep track of alert zones so the bot does not repeat
# the same alert every 5 minutes.
last_sol_zone = None
last_xrp_zone = None


# =========================================================
# TELEGRAM
# =========================================================

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram settings are missing.")
        return False

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )

        if response.status_code != 200:
            print("Telegram error:", response.text)
            return False

        return True

    except Exception as e:
        print("Telegram exception:", e)
        return False


# =========================================================
# GET CRYPTO PRICES FROM KRAKEN
# =========================================================

def get_prices():
    try:
        url = "https://api.kraken.com/0/public/Ticker"

        params = {
            "pair": "SOLCAD,XRPCAD,ETHCAD,XLMCAD"
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            if len(data["error"]) > 0:
                print("Kraken API error:", data["error"])
                return None

        result = data.get("result", {})

        prices = {}

        for pair_name, ticker in result.items():

            pair_upper = pair_name.upper()

            # Current/latest trade price
            current_price = float(ticker["c"][0])

            if "SOL" in pair_upper:
                prices["SOL"] = current_price

            elif "XRP" in pair_upper:
                prices["XRP"] = current_price

            elif "ETH" in pair_upper:
                prices["ETH"] = current_price

            elif "XLM" in pair_upper:
                prices["XLM"] = current_price

        required = ["SOL", "XRP", "ETH", "XLM"]

        missing = [
            coin for coin in required
            if coin not in prices
        ]

        if missing:
            print("Missing Kraken prices:", missing)
            print("Kraken result:", result)
            return None

        print("Prices:", prices)

        return prices

    except Exception as e:
        print("Price error:", e)
        return None


# =========================================================
# SOL ALERTS
# =========================================================

def check_sol_alert(price):
    global last_sol_zone

    if price <= SOL_BUY:
        zone = "BUY"

        if last_sol_zone != zone:
            send_message(
                "🟢 SOL BUY ALERT\n"
                f"1 SOL = C${price:.2f} CAD\n"
                f"Buy level = C${SOL_BUY:.2f} CAD"
            )

    elif price >= SOL_SELL:
        zone = "SELL"

        if last_sol_zone != zone:
            send_message(
                "🔴 SOL SELL ALERT\n"
                f"1 SOL = C${price:.2f} CAD\n"
                f"Sell level = C${SOL_SELL:.2f} CAD"
            )

    else:
