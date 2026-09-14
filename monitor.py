import os
import time
import requests

# =====================================
# SETTINGS
# =====================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHECK_EVERY_SECONDS = 300  # 5 minutes

# Alert levels in CAD
SOL_BUY = 125.00
SOL_SELL = 150.00

XRP_BUY = 1.30
XRP_SELL = 2.00

last_sol_zone = None
last_xrp_zone = None


# =====================================
# TELEGRAM
# =====================================

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram settings are missing.")
        return False

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            json={
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


# =====================================
# GET CRYPTO PRICES IN CAD
# =====================================

def get_prices():
    try:
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            "?
