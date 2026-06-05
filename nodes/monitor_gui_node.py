from dashboard_gui import DashboardGUI


def monitor_worker(input_queue):

    gui = DashboardGUI()

    while True:

        packet = input_queue.get()

        gui.update_dashboard(
            packet["total_power"],
            packet["alert"],
            packet["action"]
        )