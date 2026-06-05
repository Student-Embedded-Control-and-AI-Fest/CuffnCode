from multiprocessing import Process
from multiprocessing import Queue

from nodes.collection_node import collection_worker
from nodes.analytics_node import analytics_worker
from nodes.anomaly_node import anomaly_worker
from nodes.smart_controller import controller_worker

from dashboard_gui import DashboardGUI


def main():

    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    dashboard_queue = Queue()

    collector = Process(
        target=collection_worker,
        args=(q1,)
    )

    analytics = Process(
        target=analytics_worker,
        args=(q1, q2)
    )

    anomaly = Process(
        target=anomaly_worker,
        args=(q2, q3)
    )

    controller = Process(
        target=controller_worker,
        args=(q3, dashboard_queue)
    )

    collector.start()
    analytics.start()
    anomaly.start()
    controller.start()

    app = DashboardGUI(
        dashboard_queue
    )

    app.run()


if __name__ == "__main__":
    main()