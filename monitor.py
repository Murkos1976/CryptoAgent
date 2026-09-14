import os
import time
import requests

# =========================
# TELEGRAM SETTINGS
# =========================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Check every 5 minutes
CHECK_EVERY_SECONDS = 300


# =========================
# PRICE ALERTS IN CAD
# =========================

SOL_BUY = 125.00
SOL_SELL = 150.00

XRP_BUY = 1.30
XRP_SELL = 2.00


# Used to avoid repeating the same alert
last_sol_zone = None
last_xrp_zone = None


# =========================
# GET PRICE FROM KRAKEN
# =========================

def get_price(pair):
    url = f"https://api.kraken.com/0/public/Ticker?pair={pair}"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    if data.get("error"):
        raise Exception(data["error"])

    result = data["result"]

    key = list(result.keys())[0]

    # c[0] = current/last traded price
    price = float(result[key]["c"][0])

    return price


# =========================
# SEND TELEGRAM MESSAGE
# =========================

def send_message(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(
        f"{TG_URL}/sendMessage",
        json=payload,
        timeout=20
    )
