from flask import Flask, request, jsonify, render_template
from multiprocessing import Process, Queue
import time

app = Flask(__name__)


def worker(worker_id, tasks, result_queue):
    for task in tasks:
        time.sleep(0.1)
        result_queue.put(f"Worker {worker_id} menyelesaikan {task}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        num_tasks = int(request.form.get("tasks", 10))
        num_workers = int(request.form.get("workers", 2))

        if num_tasks < 1:
            num_tasks = 1

        if num_workers < 1:
            num_workers = 1

        tasks = [f"Tugas-{i+1}" for i in range(num_tasks)]
        chunk_size = max(1, len(tasks) // num_workers)

        result_queue = Queue()
        processes = []
        worker_distribution = {}

        start_time = time.time()

        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size

            if i == num_workers - 1:
                worker_tasks = tasks[start:]
            else:
                worker_tasks = tasks[start:end]

            worker_distribution[f"Worker {i+1}"] = len(worker_tasks)

            p = Process(target=worker, args=(i + 1, worker_tasks, result_queue))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        parallel_time = round(time.time() - start_time, 2)
        serial_time = max(1, num_tasks)
        speed_up = round(serial_time / parallel_time, 2) if parallel_time > 0 else 0
        efficiency = round((speed_up / num_workers) * 100, 2) if num_workers > 0 else 0

        return jsonify({
            "success": True,
            "results": results,
            "execution_time": parallel_time,
            "serial_time": serial_time,
            "speed_up": speed_up,
            "efficiency": efficiency,
            "total_tasks": num_tasks,
            "total_workers": num_workers,
            "worker_distribution": worker_distribution,
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        })


if __name__ == "__main__":
    app.run(debug=True)
