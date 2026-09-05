import requests

coins = ["SOL", "XRP", "ETH"]

print("CRYPTO TRADING SIGNALS")
print("----------------------")

for coin in coins:
    url = f"https://api.kraken.com/0/public/OHLC?pair={coin}USD&interval=60"
    data = requests.get(url).json()["result"]

    key = [k for k in data if k != "last"][0]
    prices = [float(x[4]) for x in data[key][-50:]]

    price = prices[-1]
    ma20 = sum(prices[-20:]) / 20
    ma50 = sum(prices) / 50

    if price > ma20 and ma20 > ma50:
        signal = "BUY"
    elif price < ma20 and ma20 < ma50:
        signal = "SELL"
    else:
        signal = "HOLD"

    print(f"{coin}: ${price:.4f} | MA20: ${ma20:.4f} | MA50: ${ma50:.4f} | SIGNAL: {signal}")