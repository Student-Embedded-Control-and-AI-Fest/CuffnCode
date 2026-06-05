def controller_worker(
    input_queue,
    dashboard_queue
):

    while True:

        packet = input_queue.get()

        action = "NO ACTION"

        if packet["alert"] == "OVERLOAD":

            action = (
                "ENABLE ECO MODE"
            )

        packet["action"] = action

        dashboard_queue.put(
            packet
        )