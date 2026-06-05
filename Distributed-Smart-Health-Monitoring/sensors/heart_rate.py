import random
import time

def heart_rate_sensor():
    while True:
        bpm = random.randint(60, 100)
        print(f"[Heart Rate] {bpm} BPM")
        time.sleep(2)