import random
import time

def temperature_sensor():
    while True:
        temp = round(random.uniform(36.0, 38.0), 1)
        print(f"[Temperature] {temp} °C")
        time.sleep(3)