import random
import time

def oxygen_sensor():
    while True:
        spo2 = random.randint(95, 100)
        print(f"[SpO2] {spo2}%")
        time.sleep(4)