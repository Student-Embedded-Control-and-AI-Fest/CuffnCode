from flask import Flask, render_template, redirect, url_for

from sensor_node import generate_sensor_data
from processor import process_data_parallel
from storage_node import save_records, read_records


app = Flask(__name__)


@app.route("/")
def index():
    """
    Menampilkan seluruh data hasil pemantauan pada dashboard.
    """

    records = read_records()

    total_records = len(records)

    high_pressure_count = sum(
        1 for record in records
        if record["blood_pressure_status"] == "High Blood Pressure"
    )

    normal_pressure_count = sum(
        1 for record in records
        if record["blood_pressure_status"] == "Normal Blood Pressure"
    )

    low_pressure_count = sum(
        1 for record in records
        if record["blood_pressure_status"] == "Low Blood Pressure"
    )

    return render_template(
        "index.html",
        records=records,
        total_records=total_records,
        high_pressure_count=high_pressure_count,
        normal_pressure_count=normal_pressure_count,
        low_pressure_count=low_pressure_count
    )


@app.route("/generate")
def generate_data():
    """
    Membuat 10 data dummy, memprosesnya secara paralel,
    lalu menyimpan hasilnya ke file CSV.
    """

    sensor_data = [generate_sensor_data() for _ in range(10)]

    processed_data = process_data_parallel(sensor_data)

    save_records(processed_data)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)