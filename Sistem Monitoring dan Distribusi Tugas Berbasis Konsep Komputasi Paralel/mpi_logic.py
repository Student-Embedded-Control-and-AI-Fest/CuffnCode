from worker import Worker


class MPISimulator:
    def __init__(self, worker_count):
        self.worker_count = worker_count
        self.workers = [
            Worker(i)
            for i in range(worker_count)
        ]

    def scatter(self, tasks):
        for index, task in enumerate(tasks):
            worker_index = index % self.worker_count
            task["worker"] = worker_index
            self.workers[worker_index].assign_task(task)

        return self.workers

    def compute(self):
        for worker in self.workers:
            worker.execute_task()

    def gather(self):
        results = []

        for worker in self.workers:
            results.extend(worker.tasks)

        return results