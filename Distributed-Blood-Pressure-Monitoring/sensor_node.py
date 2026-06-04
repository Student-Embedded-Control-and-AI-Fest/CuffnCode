import random
from datetime import datetime


def generate_sensor_data():
    """
    Simulasi data dari sensor tekanan darah.
    Data dibuat dummy karena belum menggunakan sensor asli.
    """

    systolic = random.randint(90, 160)
    diastolic = random.randint(60, 100)
    heart_rate = random.randint(60, 110)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "systolic": systolic,
        "diastolic": diastolic,
        "heart_rate": heart_rate
    }


if __name__ == "__main__":
    data = generate_sensor_data()
    print(data)