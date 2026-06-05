def anomaly_worker(input_queue, output_queue):

    while True:

        packet = input_queue.get()

        alert = "NORMAL"

        if packet["total_power"] > 2500:
            alert = "OVERLOAD"

        packet["alert"] = alert

        print("[ANOMALY]", alert)

        output_queue.put(packet)