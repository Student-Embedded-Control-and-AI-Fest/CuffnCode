from multiprocessing import Process

from sensors.heart_rate import heart_rate_sensor
from sensors.temperature import temperature_sensor
from sensors.oxygen import oxygen_sensor

if __name__ == "__main__":
    p1 = Process(target=heart_rate_sensor)
    p2 = Process(target=temperature_sensor)
    p3 = Process(target=oxygen_sensor)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()