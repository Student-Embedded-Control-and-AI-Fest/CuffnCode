from multiprocessing import Pool, cpu_count


def classify_blood_pressure(data):
    """
    Memproses satu data sensor dan menentukan status tekanan darah.
    Fungsi ini nantinya dijalankan secara paralel oleh beberapa worker.
    """

    systolic = data["systolic"]
    diastolic = data["diastolic"]
    heart_rate = data["heart_rate"]

    if systolic < 90 or diastolic < 60:
        status = "Low Blood Pressure"
    elif systolic >= 140 or diastolic >= 90:
        status = "High Blood Pressure"
    else:
        status = "Normal Blood Pressure"

    if heart_rate > 100:
        heart_rate_status = "High Heart Rate"
    elif heart_rate < 60:
        heart_rate_status = "Low Heart Rate"
    else:
        heart_rate_status = "Normal Heart Rate"

    data["blood_pressure_status"] = status
    data["heart_rate_status"] = heart_rate_status

    return data


def process_data_parallel(sensor_data_list):
    """
    Memproses banyak data sensor secara paralel menggunakan multiprocessing.
    """

    worker_count = min(cpu_count(), len(sensor_data_list))

    with Pool(processes=worker_count) as pool:
        processed_data = pool.map(classify_blood_pressure, sensor_data_list)

    return processed_data

if __name__ == "__main__":
    from sensor_node import generate_sensor_data

    dummy_data = [generate_sensor_data() for _ in range(10)]

    results = process_data_parallel(dummy_data)

    for result in results:
        print(result)