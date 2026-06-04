import csv
import os


CSV_FILE = os.path.join("data", "blood_pressure_records.csv")


def initialize_storage():
    """
    Membuat folder data dan file CSV jika belum tersedia.
    """

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "systolic",
                "diastolic",
                "heart_rate",
                "blood_pressure_status",
                "heart_rate_status"
            ])


def save_records(records):
    """
    Menyimpan banyak hasil pemrosesan ke file CSV.
    """

    initialize_storage()

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for record in records:
            writer.writerow([
                record["timestamp"],
                record["systolic"],
                record["diastolic"],
                record["heart_rate"],
                record["blood_pressure_status"],
                record["heart_rate_status"]
            ])


def read_records():
    """
    Membaca seluruh data dari file CSV.
    """

    initialize_storage()

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


if __name__ == "__main__":
    from sensor_node import generate_sensor_data
    from processor import process_data_parallel

    dummy_data = [generate_sensor_data() for _ in range(10)]

    processed_data = process_data_parallel(dummy_data)

    save_records(processed_data)

    print("Data berhasil disimpan ke:", CSV_FILE)

    records = read_records()

    for record in records:
        print(record)