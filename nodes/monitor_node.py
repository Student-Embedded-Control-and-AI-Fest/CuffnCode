import csv
import os
from datetime import datetime


def monitor_worker(input_queue):

    os.makedirs("logs", exist_ok=True)

    while True:

        packet = input_queue.get()

        print("\n")
        print("=" * 50)
        print("SMART BUILDING MONITOR")
        print("=" * 50)

        print("TOTAL POWER :", packet["total_power"])
        print("AVERAGE     :", packet["average_power"])
        print("ALERT       :", packet["alert"])
        print("ACTION      :", packet["action"])

        with open(
            "logs/energy_log.csv",
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                datetime.now(),
                packet["total_power"],
                packet["average_power"],
                packet["alert"],
                packet["action"]
            ])