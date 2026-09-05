import csv
import os
from datetime import datetime
import requests

portfolio = {
    "SOL": 19.08013866,
    "XRP": 442.1588556,
    "ETH": 0.01964033
}

file = "crypto_history.csv"
new_file = not os.path.exists(file)

with open(file, "a", newline="") as f:
    writer = csv.writer(f)

    if new_file:
        writer.writerow([
            "Date", "Coin", "Amount",
            "Price", "Value", "MA20",
            "MA50", "Signal"
        ])

    for coin, amount in portfolio.items():
        url = f"https://api.kraken.com/0/public/OHLC?pair={coin}USD&interval=60"
        data = requests.get(url).json()["result"]

        key = [k for k in data if k != "last"][0]
        prices = [float(x[4]) for x in data[key][-50:]]

        price = prices[-1]
        ma20 = sum(prices[-20:]) / 20
        ma50 = sum(prices) / 50
        value = amount * price

        if price > ma20 and ma20 > ma50:
            signal = "BUY"
        elif price < ma20 and ma20 < ma50:
            signal = "SELL"
        else:
            signal = "HOLD"

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            coin,
            amount,
            price,
            value,
            ma20,
            ma50,
            signal
        ])

        print(f"{coin}: {signal}")

print("\nHistory saved to crypto_history.csv")