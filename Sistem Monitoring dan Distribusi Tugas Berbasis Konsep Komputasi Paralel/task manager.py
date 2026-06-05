class TaskManager:

    def __init__(self):
        self.tasks = []

    def add_task(self, task_name):

        self.tasks.append({
            "name": task_name,
            "status": "Pending"
        })

    def get_tasks(self):
        return self.tasks

    def clear(self):
        self.tasks = []