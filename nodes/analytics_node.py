def analytics_worker(input_queue, output_queue):

    while True:

        data = input_queue.get()

        total = sum(data.values())

        average = total / len(data)

        result = {
            "raw_data": data,
            "total_power": total,
            "average_power": average
        }

        print("[ANALYTICS]", result)

        output_queue.put(result)