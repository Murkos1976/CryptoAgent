import requests
from rules import check_signal, decision
from analysis import calculate_rsi

portfolio = {
    "SOL": 19.08013866,
    "XRP": 442.1588556,
    "ETH": 0.01964033
}

print("==============================")
print("        CRYPTO AGENT")
print("==============================")

total = 0

for coin, amount in portfolio.items():

    url = f"https://api.kraken.com/0/public/OHLC?pair={coin}USD&interval=60"
    data = requests.get(url).json()["result"]

    key = [k for k in data if k != "last"][0]
    prices = [float(x[4]) for x in data[key][-50:]]

    price = prices[-1]
    ma20 = sum(prices[-20:]) / 20
    ma50 = sum(prices) / 50
    rsi = calculate_rsi(prices)

    value = amount * price
    total += value

    signal = check_signal(price, ma20, ma50, rsi)

    print(f"\n{coin}")
    print(f"Amount: {amount}")
    print(f"Price: ${price:.4f}")
    print(f"Value: ${value:.2f}")
    print(f"MA20: ${ma20:.4f}")
    print(f"MA50: ${ma50:.4f}")
    print(f"RSI: {rsi:.2f}")
    print(f"SIGNAL: {signal}")
    print(decision(signal))
    print(f"Current value: ${value:.2f}")

print("\n==============================")
print(f"TOTAL PORTFOLIO: ${total:.2f}")
print("==============================")