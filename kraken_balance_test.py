import os
import time
import base64
import hashlib
import hmac
import urllib.parse
import requests

API_KEY = os.environ.get("KRAKEN_API_KEY")
API_SECRET = os.environ.get("KRAKEN_API_SECRET")

API_URL = "https://api.kraken.com"
API_PATH = "/0/private/Balance"

nonce = str(int(time.time() * 1000))
data = {"nonce": nonce}
postdata = urllib.parse.urlencode(data)

message = API_PATH.encode() + hashlib.sha256(
    (nonce + postdata).encode()
).digest()

signature = base64.b64encode(
    hmac.new(
        base64.b64decode(API_SECRET),
        message,
        hashlib.sha512
    ).digest()
).decode()

headers = {
    "API-Key": API_KEY,
    "API-Sign": signature
}

response = requests.post(
    API_URL + API_PATH,
    headers=headers,
    data=data,
    timeout=20
)

result = response.json()

if result.get("error"):
    print("Kraken API error:", result["error"])
else:
    balances = result.get("result", {})
    cad = balances.get("CAD", balances.get("ZCAD", "0"))

    print("Kraken connection: OK")
    print(f"CAD balance: C${float(cad):.2f}")
