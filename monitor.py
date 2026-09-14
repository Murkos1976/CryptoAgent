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
            "?ids=solana,ripple,ethereum,stellar"
            "&vs_currencies=cad"
        )

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()

        prices = {
            "SOL": float(data["solana"]["cad"]),
            "XRP": float(data["ripple"]["cad"]),
            "ETH": float(data["ethereum"]["cad"]),
            "XLM": float(data["stellar"]["cad"])
        }

        return prices

    except Exception as e:
        print("Price error:", e)
        return None


# =====================================
# SOL ALERTS
# =====================================

def check_sol_alert(price):
    global last_sol_zone

    if price <= SOL_BUY:
        zone = "BUY"

        if last_sol_zone != zone:
            send_message(
                "🟢 SOL BUY ALERT\n\n"
                f"1 SOL = C${price:.2f} CAD\n"
                f"Buy level = C${SOL_BUY:.2f} CAD"
            )

    elif price >= SOL_SELL:
        zone = "SELL"

        if last_sol_zone != zone:
            send_message(
                "🔴 SOL SELL ALERT\n\n"
                f"1 SOL = C${price:.2f} CAD\n"
                f"Sell level = C${SOL_SELL:.2f} CAD"
            )

    else:
        zone = "NORMAL"

    last_sol_zone = zone


# =====================================
# XRP ALERTS
# =====================================

def check_xrp_alert(price):
    global last_xrp_zone

    if price <= XRP_BUY:
        zone = "BUY"

        if last_xrp_zone != zone:
            send_message(
                "🟢 XRP BUY ALERT\n\n"
                f"1 XRP = C${price:.4f} CAD\n"
                f"Buy level = C${XRP_BUY:.2f} CAD"
            )

    elif price >= XRP_SELL:
        zone = "SELL"

        if last_xrp_zone != zone:
            send_message(
                "🔴 XRP SELL ALERT\n\n"
                f"1 XRP = C${price:.4f} CAD\n"
                f"Sell level = C${XRP_SELL:.2f} CAD"
            )

    else:
        zone = "NORMAL"

    last_xrp_zone = zone


# =====================================
# MAIN LOOP
# =====================================

def main():
    print("CryptoAgent starting...")

    send_message(
        "✅ CryptoAgent started\n\n"
        "Tracking:\n"
        "SOL\n"
        "XRP\n"
        "ETH\n"
        "XLM\n\n"
        "Currency: CAD 🇨🇦\n"
        "Update every 5 minutes."
    )

    while True:
        try:
            prices = get_prices()

            if prices:
                sol = prices["SOL"]
                xrp = prices["XRP"]
                eth = prices["ETH"]
                xlm = prices["XLM"]

                message = (
                    "📊 CRYPTO PRICE UPDATE\n\n"
                    f"1 SOL = C${sol:.2f} CAD\n"
                    f"1 XRP = C${xrp:.4f} CAD\n"
                    f"1 ETH = C${eth:.2f} CAD\n"
                    f"1 XLM = C${xlm:.4f} CAD\n\n"
                    "Next check in 5 minutes."
                )

                send_message(message)

                check_sol_alert(sol)
                check_xrp_alert(xrp)

            else:
                print("No price data. Will try again in 5 minutes.")

        except Exception as e:
            print("Main loop error:", e)

        time.sleep(CHECK_EVERY_SECONDS)


# =====================================
# START
# =====================================
    main()
