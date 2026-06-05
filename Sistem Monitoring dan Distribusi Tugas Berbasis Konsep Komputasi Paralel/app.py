from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import json
import random
from datetime import datetime

app = Flask(__name__)

DATA_DIR = "data"
TASK_FILE = os.path.join(DATA_DIR, "tasks.json")
LOG_FILE = os.path.join(DATA_DIR, "logs.json")

workers_count = 4
is_running = False


def init_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as file:
            json.dump([], file)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as file:
            json.dump([], file)


def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().strip()

            if content == "":
                return []

            return json.loads(content)

    except:
        return []


def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def load_tasks():
    return load_json(TASK_FILE)


def save_tasks(tasks):
    save_json(TASK_FILE, tasks)


def load_logs():
    return load_json(LOG_FILE)


def save_log(message):
    logs = load_logs()

    logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message
    })

    save_json(LOG_FILE, logs)


def distribute_tasks(tasks):
    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    sorted_tasks = sorted(
        tasks,
        key=lambda task: priority_order.get(task.get("priority", "Low"), 4)
    )

    distributed = [[] for _ in range(workers_count)]

    for index, task in enumerate(sorted_tasks):
        worker_id = index % workers_count
        task["worker"] = worker_id
        distributed[worker_id].append(task)

    return distributed


def calculate_worker_progress(distributed):
    result = []

    for worker_id, worker_tasks in enumerate(distributed):
        total = len(worker_tasks)

        done = len([
            task for task in worker_tasks
            if task["status"] == "Done"
        ])

        progress = int((done / total) * 100) if total > 0 else 0

        result.append({
            "worker": worker_id,
            "total": total,
            "done": done,
            "progress": progress
        })

    return result


def calculate_worker_performance(distributed):
    performance = []

    for worker_id, worker_tasks in enumerate(distributed):
        total = len(worker_tasks)

        pending = len([
            task for task in worker_tasks
            if task["status"] == "Pending"
        ])

        running = len([
            task for task in worker_tasks
            if task["status"] == "Running"
        ])

        done = len([
            task for task in worker_tasks
            if task["status"] == "Done"
        ])

        total_estimate = 0

        for task in worker_tasks:
            try:
                total_estimate += int(task.get("estimate", 0))
            except:
                total_estimate += 0

        efficiency = int((done / total) * 100) if total > 0 else 0

        performance.append({
            "worker": worker_id,
            "total": total,
            "pending": pending,
            "running": running,
            "done": done,
            "estimate": total_estimate,
            "efficiency": efficiency
        })

    return performance


def get_next_task_id(tasks):
    if not tasks:
        return 1

    return max(task["id"] for task in tasks) + 1


@app.route("/", methods=["GET", "POST"])
def index():
    global workers_count
    global is_running

    init_data()

    tasks = load_tasks()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            task_name = request.form.get("task")
            category = request.form.get("category")
            priority = request.form.get("priority")
            estimate = request.form.get("estimate")

            if not estimate:
                estimate = "5"

            if task_name:
                tasks.append({
                    "id": get_next_task_id(tasks),
                    "name": task_name,
                    "category": category,
                    "priority": priority,
                    "estimate": estimate,
                    "status": "Pending",
                    "worker": "-"
                })

                save_tasks(tasks)
                save_log(f"Task ditambahkan: {task_name}")

        elif action == "set_worker":
            workers_count = int(request.form.get("workers"))
            save_log(f"Jumlah worker diubah menjadi {workers_count}")

        elif action == "start":
            is_running = True

            for task in tasks:
                if task["status"] == "Pending":
                    task["status"] = random.choice(["Running", "Done"])

            save_tasks(tasks)
            save_log("Priority Scheduler aktif. Task High diproses terlebih dahulu.")
            save_log("MPI Scatter dijalankan. Task didistribusikan ke worker.")

        elif action == "step":
            priority_order = {
                "High": 1,
                "Medium": 2,
                "Low": 3
            }

            sorted_tasks = sorted(
                tasks,
                key=lambda task: priority_order.get(task.get("priority", "Low"), 4)
            )

            for task in sorted_tasks:
                if task["status"] == "Pending":
                    task["status"] = "Running"
                    save_log(f"Task masuk proses Running: {task['name']}")
                    break

                elif task["status"] == "Running":
                    task["status"] = "Done"
                    save_log(f"Task selesai diproses: {task['name']}")
                    break

            save_tasks(tasks)

        elif action == "refresh":
            for task in tasks:
                if task["status"] == "Running":
                    task["status"] = random.choice(["Running", "Done"])

            save_tasks(tasks)
            save_log("Status worker diperbarui.")

        elif action == "reset_status":
            for task in tasks:
                task["status"] = "Pending"
                task["worker"] = "-"

            is_running = False
            save_tasks(tasks)
            save_log("Semua status task dikembalikan ke Pending.")

        elif action == "reset_all":
            save_tasks([])
            save_json(LOG_FILE, [])
            is_running = False

        elif action == "delete":
            task_id = int(request.form.get("task_id"))

            tasks = [
                task for task in tasks
                if task["id"] != task_id
            ]

            save_tasks(tasks)
            save_log(f"Task ID {task_id} dihapus.")

        return redirect(url_for("index"))

    distributed = distribute_tasks(tasks)
    save_tasks(tasks)

    total_tasks = len(tasks)

    pending_count = len([
        task for task in tasks
        if task["status"] == "Pending"
    ])

    running_count = len([
        task for task in tasks
        if task["status"] == "Running"
    ])

    done_count = len([
        task for task in tasks
        if task["status"] == "Done"
    ])

    high_priority_count = len([
        task for task in tasks
        if task.get("priority") == "High"
    ])

    progress = int((done_count / total_tasks) * 100) if total_tasks > 0 else 0

    worker_progress = calculate_worker_progress(distributed)
    worker_performance = calculate_worker_performance(distributed)

    logs = load_logs()

    return render_template(
        "index.html",
        tasks=tasks,
        distributed=distributed,
        worker_progress=worker_progress,
        worker_performance=worker_performance,
        workers_count=workers_count,
        total_tasks=total_tasks,
        pending_count=pending_count,
        running_count=running_count,
        done_count=done_count,
        high_priority_count=high_priority_count,
        progress=progress,
        logs=logs[-10:],
        is_running=is_running
    )


@app.route("/export")
def export():
    init_data()

    return send_file(
        TASK_FILE,
        as_attachment=True
    )


if __name__ == "__main__":
    init_data()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )