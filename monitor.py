import time
import subprocess
from datetime import datetime

while True:
    print(f"\n[{datetime.now()}] Running CryptoAgent...")
    
    try:
        subprocess.run(["python", "agent.py"])
    except Exception as e:
        print("Error:", e)

    print("Next check in 5 minutes...")
    time.sleep(300)
