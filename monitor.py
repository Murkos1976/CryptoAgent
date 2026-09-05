import time
import subprocess
import requests
import os
import sys

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram settings are missing.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    for i in range(0, len(message), 4000):
        data = {
            "chat_id": CHAT_ID,
            "text": message[i:i + 4000]
        }

        try:
            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                print("Telegram alert sent.")
            else:
                print("Telegram error:", response.text)

        except Exception as e:
            print("Telegram error:", e)


print("==============================")
print("      CRYPTO AGENT MONITOR")
print("==============================")
print("Checking every 5 minutes...")
print("Press Ctrl+C to stop.")


while True:

    print("\n==============================")
    print("NEW MARKET CHECK")
    print("==============================")

    result = subprocess.run(
        [sys.executable, "agent.py"],
        capture_output=True,
        text=True
    )

    output = result.stdout
    print(output)

    message = (
        "🚨 CRYPTO AGENT UPDATE 🚨\n\n"
        + output
        + "\nNext check in 5 minutes."
    )

    send_telegram(message)

    print("\nSaving market history...")

    subprocess.run(
        [sys.executable, "history.py"]
    )

    print("\nNext check in 5 minutes...")
    time.sleep(300)