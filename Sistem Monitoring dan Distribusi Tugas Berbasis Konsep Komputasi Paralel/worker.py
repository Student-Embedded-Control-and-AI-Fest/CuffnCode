class Worker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.tasks = []

    def assign_task(self, task):
        self.tasks.append(task)

    def execute_task(self):
        for task in self.tasks:
            if task["status"] == "Pending":
                task["status"] = "Running"
            elif task["status"] == "Running":
                task["status"] = "Done"

    def get_progress(self):
        total = len(self.tasks)
        done = len([
            task for task in self.tasks
            if task["status"] == "Done"
        ])

        if total == 0:
            return 0

        return int((done / total) * 100)