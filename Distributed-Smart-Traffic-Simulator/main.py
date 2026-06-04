from multiprocessing import Process
from multiprocessing import Queue

from nodes.acquisition_node import (
    acquisition_node
)

from nodes.analysis_node import (
    analysis_node
)

from nodes.controller_node import (
    controller_node
)

from nodes.dashboard_node import (
    dashboard_node
)


def main():

    q1 = Queue()
    q2 = Queue()
    q3 = Queue()

    p1 = Process(
        target=acquisition_node,
        args=(q1,)
    )

    p2 = Process(
        target=analysis_node,
        args=(q1, q2)
    )

    p3 = Process(
        target=controller_node,
        args=(q2, q3)
    )

    p4 = Process(
        target=dashboard_node,
        args=(q3,)
    )

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()


if __name__ == "__main__":
    main()