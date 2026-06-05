import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from collections import deque


class DashboardGUI:

    def __init__(self, dashboard_queue):

        self.queue = dashboard_queue

        self.root = tk.Tk()

        self.root.title(
            "Smart Building Energy Management"
        )

        self.root.geometry("1000x700")

        title = ttk.Label(
            self.root,
            text="SMART BUILDING ENERGY MANAGEMENT",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=10)

        info_frame = ttk.Frame(self.root)
        info_frame.pack(pady=10)

        self.total_label = ttk.Label(
            info_frame,
            text="Total Power : 0 W",
            font=("Arial", 12)
        )

        self.total_label.grid(
            row=0,
            column=0,
            padx=20
        )

        self.alert_label = ttk.Label(
            info_frame,
            text="Alert : NORMAL",
            font=("Arial", 12)
        )

        self.alert_label.grid(
            row=0,
            column=1,
            padx=20
        )

        self.action_label = ttk.Label(
            info_frame,
            text="Action : NONE",
            font=("Arial", 12)
        )

        self.action_label.grid(
            row=0,
            column=2,
            padx=20
        )

        self.history = deque(maxlen=30)

        self.figure = Figure(
            figsize=(8,4),
            dpi=100
        )

        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(
            "Real-Time Total Power Consumption"
        )

        self.ax.set_xlabel("Time")

        self.ax.set_ylabel("Power (Watt)")

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.root
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack()

        self.device_table = ttk.Treeview(
            self.root,
            columns=("Power"),
            show="headings",
            height=5
        )

        self.device_table.heading(
            "Power",
            text="Power (W)"
        )

        self.device_table.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.device_table.insert(
            "",
            "end",
            iid="hvac",
            values=(0,)
        )

        self.device_table.insert(
            "",
            "end",
            iid="lighting",
            values=(0,)
        )

        self.device_table.insert(
            "",
            "end",
            iid="elevator",
            values=(0,)
        )

        self.device_table.insert(
            "",
            "end",
            iid="server",
            values=(0,)
        )

        self.device_table.insert(
            "",
            "end",
            iid="solar",
            values=(0,)
        )

        self.root.after(
            1000,
            self.update_dashboard
        )

    def update_dashboard(self):

        while not self.queue.empty():

            packet = self.queue.get()

            total = packet["total_power"]

            self.total_label.config(
                text=f"Total Power : {total} W"
            )

            self.alert_label.config(
                text=f"Alert : {packet['alert']}"
            )

            self.action_label.config(
                text=f"Action : {packet['action']}"
            )

            raw = packet["raw_data"]

            self.device_table.item(
                "hvac",
                values=(raw["hvac"],)
            )

            self.device_table.item(
                "lighting",
                values=(raw["lighting"],)
            )

            self.device_table.item(
                "elevator",
                values=(raw["elevator"],)
            )

            self.device_table.item(
                "server",
                values=(raw["server"],)
            )

            self.device_table.item(
                "solar",
                values=(raw["solar"],)
            )

            self.history.append(total)

            self.ax.clear()

            self.ax.plot(
                list(self.history)
            )

            self.ax.set_title(
                "Real-Time Total Power Consumption"
            )

            self.ax.set_ylabel(
                "Power (W)"
            )

            self.canvas.draw()

        self.root.after(
            1000,
            self.update_dashboard
        )

    def run(self):

        self.root.mainloop()