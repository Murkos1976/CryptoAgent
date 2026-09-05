def check_signal(price, ma20, ma50, rsi):

    if price > ma20 and ma20 > ma50 and 50 <= rsi < 70:
        return "BUY"

    elif price < ma20 and ma20 < ma50 and 30 < rsi <= 50:
        return "SELL"

    else:
        return "HOLD"


def decision(signal):
    return f"{signal} SIGNAL"