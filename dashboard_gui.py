import sys
import os
import csv
import random
import time
import threading
from queue import Empty

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QProgressBar,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStatusBar,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ----------------------------------------------------
# WIDGET DEFINITIONS
# ----------------------------------------------------

class LEDIndicator(QWidget):
    """Circular glowing LED indicator widget."""
    def __init__(self, size=14, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.color = "#374151"  # Default gray
        self.set_color(self.color)

    def set_color(self, hex_color):
        self.color = hex_color
        # Apply 3D-like radial gradient for glowing LED effect
        self.setStyleSheet(f"""
            background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.3, fy:0.3, 
                stop:0 #FFFFFF, stop:0.3 {hex_color}, stop:1 #000000);
            border-radius: {self.size // 2}px;
            border: 1px solid #000000;
        """)


class PipelineNodeBox(QLabel):
    """Representing a Node or Queue inside the system architecture flow diagram."""
    def __init__(self, text, is_node=True, parent=None):
        super().__init__(text, parent)
        self.is_node = is_node
        self.setAlignment(Qt.AlignCenter)
        self.set_state(active=False)
        self.setFixedHeight(35 if is_node else 25)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_state(self, active=False):
        if self.is_node:
            if active:
                # Active highlighted state (bright neon blue cyan)
                self.setStyleSheet("""
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #0EA5E9);
                    color: #0F172A;
                    font-weight: bold;
                    border: 2px solid #38BDF8;
                    border-radius: 6px;
                    font-size: 11px;
                """)
            else:
                # Normal state
                self.setStyleSheet("""
                    background-color: #1E293B;
                    color: #E2E8F0;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    font-size: 11px;
                """)
        else:  # Queue representation
            if active:
                # Active highlighted queue (yellow/orange glow)
                self.setStyleSheet("""
                    background-color: #F59E0B;
                    color: #0F172A;
                    font-weight: bold;
                    border: 1.5px solid #FCD34D;
                    border-radius: 4px;
                    font-size: 10px;
                """)
            else:
                self.setStyleSheet("""
                    background-color: #0F172A;
                    color: #94A3B8;
                    border: 1px solid #1E293B;
                    border-radius: 4px;
                    font-size: 10px;
                """)


class LaneCard(QFrame):
    """Individual card for each lane showing real-time statistics."""
    def __init__(self, lane_id, display_name, parent=None):
        super().__init__(parent)
        self.setObjectName("LaneCard")
        self.lane_id = lane_id
        self.display_name = display_name
        self.init_ui()

    def init_ui(self):
        # Card style
        self.setStyleSheet("""
            QFrame#LaneCard {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header (Lane Name)
        self.name_label = QLabel(self.display_name)
        self.name_label.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: bold; letter-spacing: 1px;")

        # Vehicle Count Display
        count_layout = QHBoxLayout()
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("color: #F8FAFC; font-size: 36px; font-weight: bold;")
        count_unit = QLabel("Vehicles")
        count_unit.setStyleSheet("color: #64748B; font-size: 14px; margin-bottom: 6px;")
        count_unit.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        count_layout.addWidget(self.count_label)
        count_layout.addWidget(count_unit)
        count_layout.addStretch()

        # Details Row (Density and Green Time Allocation)
        details_layout = QHBoxLayout()

        # Density Status
        density_title = QLabel("Density:")
        density_title.setStyleSheet("color: #64748B; font-size: 11px;")
        self.density_val = QLabel("LOW")
        self.density_val.setStyleSheet("color: #10B981; font-size: 12px; font-weight: bold;")

        # Green Time Allocation
        green_title = QLabel("Green Time:")
        green_title.setStyleSheet("color: #64748B; font-size: 11px; margin-left: 15px;")
        self.green_val = QLabel("0 sec")
        self.green_val.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: bold;")

        details_layout.addWidget(density_title)
        details_layout.addWidget(self.density_val)
        details_layout.addWidget(green_title)
        details_layout.addWidget(self.green_val)
        details_layout.addStretch()

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 30)
        self.progress_bar.setValue(0)
        self.set_progress_style("LOW")

        layout.addWidget(self.name_label)
        layout.addLayout(count_layout)
        layout.addLayout(details_layout)
        layout.addWidget(self.progress_bar)

    def set_progress_style(self, density):
        # Color mapping: LOW (Green), MEDIUM (Yellow), HIGH (Red)
        if density == "LOW":
            color = "#10B981"
            txt_color = "#10B981"
        elif density == "MEDIUM":
            color = "#F59E0B"
            txt_color = "#F59E0B"
        else:
            color = "#EF4444"
            txt_color = "#EF4444"

        self.density_val.setText(density)
        self.density_val.setStyleSheet(f"color: {txt_color}; font-size: 12px; font-weight: bold;")

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #1E293B;
                border-radius: 6px;
                background-color: #0F172A;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 10px;
                height: 14px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def update_data(self, vehicle_count, density, green_time):
        self.count_label.setText(str(vehicle_count))
        self.green_val.setText(f"{green_time} sec")
        self.progress_bar.setValue(vehicle_count)
        self.set_progress_style(density)


class RealtimeChart(FigureCanvas):
    """Matplotlib widget for plotting historical lane density."""
    def __init__(self, parent=None):
        # Create dark-themed matplotlib figure
        self.fig = Figure(figsize=(5, 3), dpi=100, facecolor='#131B2E')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#131B2E')

        # Format axes spines
        for spine in self.axes.spines.values():
            spine.set_color('#1E293B')

        # Tick & Grid settings
        self.axes.tick_params(colors='#94A3B8', labelsize=8)
        self.axes.grid(True, color='#1E293B', linestyle='--', alpha=0.5)

        self.axes.set_title("Vehicle History (Last 10 Cycles)", color='#E2E8F0', fontsize=9, fontweight='bold', pad=8)
        self.axes.set_ylabel("Vehicle Count", color='#94A3B8', fontsize=8)

        super().__init__(self.fig)
        self.setParent(parent)

        # Historical data registers
        self.history_len = 10
        self.x_data = list(range(self.history_len))
        self.data_history = {
            "lane1": [0] * self.history_len,
            "lane2": [0] * self.history_len,
            "lane3": [0] * self.history_len,
            "lane4": [0] * self.history_len,
        }

        # Lane colors matches UI accents
        self.colors = {
            "lane1": "#0EA5E9",  # Cyan
            "lane2": "#10B981",  # Green
            "lane3": "#F59E0B",  # Yellow
            "lane4": "#EF4444",  # Red
        }

        self.lines = {}
        for lane in ["lane1", "lane2", "lane3", "lane4"]:
            display_name = lane.replace("lane", "Lane ")
            self.lines[lane], = self.axes.plot(
                self.x_data,
                self.data_history[lane],
                color=self.colors[lane],
                label=display_name,
                linewidth=2
            )

        # Legend with dark background
        self.legend = self.axes.legend(
            loc='upper left',
            facecolor='#0F172A',
            edgecolor='#1E293B',
            fontsize=8
        )
        for text in self.legend.get_texts():
            text.set_color('#E2E8F0')

        self.axes.set_ylim(-1, 35)
        self.fig.tight_layout()

    def update_chart(self, new_data):
        for lane in ["lane1", "lane2", "lane3", "lane4"]:
            val = new_data.get(lane, {}).get("vehicles", 0)
            self.data_history[lane].pop(0)
            self.data_history[lane].append(val)
            self.lines[lane].set_ydata(self.data_history[lane])

        self.axes.relim()
        self.axes.autoscale_view(scalex=False, scaley=True)
        self.axes.set_ylim(-1, 35)
        self.draw()


# ----------------------------------------------------
# MAIN DASHBOARD WINDOW
# ----------------------------------------------------

class DashboardWindow(QMainWindow):
    def __init__(self, queue_in=None):
        super().__init__()
        self.queue_in = queue_in
        self.is_live_mode = queue_in is not None
        
        # Window attributes
        self.setWindowTitle("Distributed Smart Traffic Control System")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #090D16;")

        # Setup main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        self.init_ui()

        # Core logic timers
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self.run_simulation_step)

        self.queue_timer = QTimer(self)
        self.queue_timer.timeout.connect(self.check_queue_step)

        # Pipeline Animation Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.on_anim_timer_tick)
        self.anim_step = 0
        self.anim_data = None

        # Start execution loop
        if self.is_live_mode:
            self.set_mode(live=True)
        else:
            self.set_mode(live=False)

        # Benchmark State and Timer
        self.benchmark_running = False
        self.perf_timer = QTimer(self)
        self.perf_timer.timeout.connect(self.trigger_benchmark_check)
        self.perf_timer.start(30000)  # Every 30 seconds
        QTimer.singleShot(1500, self.trigger_benchmark_check)  # Run once after UI is shown

        # Analytics and Logging state
        self.update_timestamps = []

    def init_ui(self):
        # Create left column layout (Dashboard Info, Lanes Grid, Matplotlib Chart)
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # --- Header ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_layout = QVBoxLayout()
        title_label = QLabel("DISTRIBUTED SMART TRAFFIC CONTROL SYSTEM")
        title_label.setStyleSheet("color: #0EA5E9; font-size: 22px; font-weight: bold; letter-spacing: 1px;")
        subtitle_label = QLabel("Parallel Computing & Distributed System Simulation")
        subtitle_label.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # Mode controls
        mode_layout = QHBoxLayout()
        self.btn_live = QPushButton("LIVE QUEUE MODE")
        self.btn_live.setCheckable(True)
        self.btn_live.clicked.connect(lambda: self.set_mode(live=True))
        
        self.btn_sim = QPushButton("STANDALONE SIMULATION")
        self.btn_sim.setCheckable(True)
        self.btn_sim.clicked.connect(lambda: self.set_mode(live=False))

        # Base style for source toggles
        toggle_style = """
            QPushButton {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid #334155;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #0EA5E9;
                color: #090D16;
                border: 1px solid #38BDF8;
            }
            QPushButton:hover {
                border: 1px solid #0EA5E9;
            }
        """
        self.btn_live.setStyleSheet(toggle_style)
        self.btn_sim.setStyleSheet(toggle_style)

        mode_layout.addWidget(self.btn_live)
        mode_layout.addWidget(self.btn_sim)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(mode_layout)

        # --- Lanes Grid (2x2) ---
        lanes_widget = QWidget()
        self.grid_layout = QGridLayout(lanes_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(15)

        self.cards = {
            "lane1": LaneCard("lane1", "LANE 1 - NORTHBOUND"),
            "lane2": LaneCard("lane2", "LANE 2 - EASTBOUND"),
            "lane3": LaneCard("lane3", "LANE 3 - SOUTHBOUND"),
            "lane4": LaneCard("lane4", "LANE 4 - WESTBOUND"),
        }
        self.grid_layout.addWidget(self.cards["lane1"], 0, 0)
        self.grid_layout.addWidget(self.cards["lane2"], 0, 1)
        self.grid_layout.addWidget(self.cards["lane3"], 1, 0)
        self.grid_layout.addWidget(self.cards["lane4"], 1, 1)

        # --- Chart Container ---
        chart_widget = QFrame()
        chart_widget.setStyleSheet("""
            QFrame {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        
        self.realtime_chart = RealtimeChart()
        chart_layout.addWidget(self.realtime_chart)

        # Add all to left column
        left_layout.addWidget(header_widget)
        left_layout.addWidget(lanes_widget, stretch=3)
        left_layout.addWidget(chart_widget, stretch=2)

        # Create right column layout (Node Status LEDs, Architecture Flow, Statistics)
        right_column = QWidget()
        right_column.setFixedWidth(380)
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # --- Panel 1: Node Status LEDs ---
        led_widget = QFrame()
        led_widget.setObjectName("RightPanel")
        led_widget.setStyleSheet("""
            QFrame#RightPanel {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        led_layout = QVBoxLayout(led_widget)
        led_layout.setContentsMargins(16, 16, 16, 16)
        led_layout.setSpacing(12)

        led_title = QLabel("SYSTEM NODE STATUS")
        led_title.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: bold; letter-spacing: 0.5px;")
        led_layout.addWidget(led_title)

        # Row lists for LEDs
        self.led_a = LEDIndicator(14)
        self.led_b = LEDIndicator(14)
        self.led_c = LEDIndicator(14)
        self.led_d = LEDIndicator(14)

        led_nodes = [
            (self.led_a, "Node A (Acquisition Process)"),
            (self.led_b, "Node B (Analysis Process)"),
            (self.led_c, "Node C (Controller Process)"),
            (self.led_d, "Node D (Dashboard Process)")
        ]
        for led, label_text in led_nodes:
            row = QHBoxLayout()
            row.addWidget(led)
            row.addSpacing(10)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
            row.addWidget(lbl)
            row.addStretch()
            led_layout.addLayout(row)

        # --- Panel 2: System Architecture ---
        arch_widget = QFrame()
        arch_widget.setObjectName("RightPanel")
        arch_widget.setStyleSheet("""
            QFrame#RightPanel {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        arch_layout = QVBoxLayout(arch_widget)
        arch_layout.setContentsMargins(16, 16, 16, 16)
        arch_layout.setSpacing(6)

        arch_title = QLabel("DISTRIBUTED PIPELINE WORKFLOW")
        arch_title.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 4px;")
        arch_layout.addWidget(arch_title)

        # Pipeline diagram definitions
        self.node_a_box = PipelineNodeBox("NODE A: TRAFFIC ACQUISITION (Acquires real-time frame rates)")
        self.arrow_1 = QLabel("▼")
        self.q1_box = PipelineNodeBox("QUEUE 1 (IPC: Multiprocessing Queue)", is_node=False)
        self.arrow_2 = QLabel("▼")
        self.node_b_box = PipelineNodeBox("NODE B: TRAFFIC ANALYSIS (Calculates Density Levels)")
        self.arrow_3 = QLabel("▼")
        self.q2_box = PipelineNodeBox("QUEUE 2 (IPC: Multiprocessing Queue)", is_node=False)
        self.arrow_4 = QLabel("▼")
        self.node_c_box = PipelineNodeBox("NODE C: ADAPTIVE CONTROLLER (Determines Green-Light Timing)")
        self.arrow_5 = QLabel("▼")
        self.q3_box = PipelineNodeBox("QUEUE 3 (IPC: Multiprocessing Queue)", is_node=False)
        self.arrow_6 = QLabel("▼")
        self.node_d_box = PipelineNodeBox("NODE D: REALTIME MONITOR (Fills Dashboard Canvas)")

        # Center arrows and apply style
        arrow_style = "color: #475569; font-size: 12px;"
        for arrow in [self.arrow_1, self.arrow_2, self.arrow_3, self.arrow_4, self.arrow_5, self.arrow_6]:
            arrow.setAlignment(Qt.AlignCenter)
            arrow.setStyleSheet(arrow_style)

        # Add all to layout
        arch_layout.addWidget(self.node_a_box)
        arch_layout.addWidget(self.arrow_1)
        arch_layout.addWidget(self.q1_box)
        arch_layout.addWidget(self.arrow_2)
        arch_layout.addWidget(self.node_b_box)
        arch_layout.addWidget(self.arrow_3)
        arch_layout.addWidget(self.q2_box)
        arch_layout.addWidget(self.arrow_4)
        arch_layout.addWidget(self.node_c_box)
        arch_layout.addWidget(self.arrow_5)
        arch_layout.addWidget(self.q3_box)
        arch_layout.addWidget(self.arrow_6)
        arch_layout.addWidget(self.node_d_box)

        # --- Panel 3: Statistics Panel ---
        stats_widget = QFrame()
        stats_widget.setObjectName("RightPanel")
        stats_widget.setStyleSheet("""
            QFrame#RightPanel {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(16, 16, 16, 16)
        stats_layout.setSpacing(10)

        stats_title = QLabel("SYSTEM STATISTICS")
        stats_title.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: bold; letter-spacing: 0.5px;")
        stats_layout.addWidget(stats_title)

        # Stats sub cards
        grid_stats = QGridLayout()
        grid_stats.setSpacing(10)

        self.stat_total_vehicles = self.create_stat_subcard("TOTAL VEHICLES", "0")
        self.stat_avg_density = self.create_stat_subcard("AVG DENSITY", "LOW")
        self.stat_active_lane = self.create_stat_subcard("ACTIVE LANE", "NONE")
        self.stat_green_time = self.create_stat_subcard("ACTIVE GREEN TIME", "0 sec")

        grid_stats.addWidget(self.stat_total_vehicles, 0, 0)
        grid_stats.addWidget(self.stat_avg_density, 0, 1)
        grid_stats.addWidget(self.stat_active_lane, 1, 0)
        grid_stats.addWidget(self.stat_green_time, 1, 1)

        stats_layout.addLayout(grid_stats)

        # --- Panel 4: Parallel Performance Panel ---
        perf_widget = QFrame()
        perf_widget.setObjectName("RightPanel")
        perf_widget.setStyleSheet("""
            QFrame#RightPanel {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        perf_layout = QVBoxLayout(perf_widget)
        perf_layout.setContentsMargins(16, 16, 16, 16)
        perf_layout.setSpacing(8)

        perf_title = QLabel("PARALLEL PERFORMANCE")
        perf_title.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 2px;")
        perf_layout.addWidget(perf_title)

        grid_perf = QGridLayout()
        grid_perf.setSpacing(6)

        def add_perf_row(label_text, row_idx):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
            val = QLabel("Calculating...")
            val.setStyleSheet("color: #E2E8F0; font-size: 11px; font-weight: bold;")
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid_perf.addWidget(lbl, row_idx, 0)
            grid_perf.addWidget(val, row_idx, 1)
            return val

        self.lbl_seq_time = add_perf_row("Sequential Time", 0)
        self.lbl_par_time = add_perf_row("Parallel Time", 1)
        self.lbl_speedup = add_perf_row("Speedup", 2)
        self.lbl_efficiency = add_perf_row("Efficiency", 3)
        self.lbl_workers = add_perf_row("CPU Workers", 4)

        perf_layout.addLayout(grid_perf)

        # Assemble right column
        right_layout.addWidget(led_widget, stretch=1)
        right_layout.addWidget(arch_widget, stretch=3)
        right_layout.addWidget(stats_widget, stretch=2)
        right_layout.addWidget(perf_widget, stretch=2)

        # --- Panel 5: Traffic Analytics Panel ---
        analytics_widget = QFrame()
        analytics_widget.setObjectName("RightPanel")
        analytics_widget.setStyleSheet("""
            QFrame#RightPanel {
                background-color: #131B2E;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)
        analytics_layout = QVBoxLayout(analytics_widget)
        analytics_layout.setContentsMargins(16, 16, 16, 16)
        analytics_layout.setSpacing(8)

        analytics_title = QLabel("TRAFFIC ANALYTICS")
        analytics_title.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 2px;")
        analytics_layout.addWidget(analytics_title)

        grid_analytics = QGridLayout()
        grid_analytics.setSpacing(6)

        def add_analytics_row(label_text, row_idx):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
            val = QLabel("N/A")
            val.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: bold;")
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid_analytics.addWidget(lbl, row_idx, 0)
            grid_analytics.addWidget(val, row_idx, 1)
            return val

        self.lbl_peak_lane = add_analytics_row("Peak Traffic Lane", 0)
        self.lbl_avg_vehicles = add_analytics_row("Average Vehicles", 1)
        self.lbl_highest_density_lane = add_analytics_row("Highest Density Lane", 2)
        self.lbl_throughput = add_analytics_row("System Throughput", 3)

        analytics_layout.addLayout(grid_analytics)

        right_layout.addWidget(analytics_widget, stretch=2)

        # Add left and right column to main layout
        self.main_layout.addWidget(left_column, stretch=3)
        self.main_layout.addWidget(right_column, stretch=1)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0F172A;
                color: #94A3B8;
                font-size: 10px;
                border-top: 1px solid #1E293B;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System initialized. Select mode to begin.")

    def create_stat_subcard(self, title, val):
        """Helper to create stats display slots."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: 1.5px solid #1E293B;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #64748B; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;")
        t_lbl.setAlignment(Qt.AlignCenter)

        v_lbl = QLabel(val)
        v_lbl.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: bold;")
        v_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        
        # Save reference to the value label on the container frame
        card.value_label = v_lbl
        return card

    # ----------------------------------------------------
    # MODE TOGGLE CONTROLLER
    # ----------------------------------------------------

    def set_mode(self, live=True):
        self.is_live_mode = live
        if live:
            self.btn_live.setChecked(True)
            self.btn_sim.setChecked(False)
            self.sim_timer.stop()
            
            # Reset LEDs to active state (glowing) since processes are running
            self.led_a.set_color("#10B981")
            self.led_b.set_color("#10B981")
            self.led_c.set_color("#10B981")
            self.led_d.set_color("#10B981")

            self.status_bar.showMessage("LIVE QUEUE MODE: Polling multiprocessing Node C queue...")
            self.queue_timer.start(100)  # Poll queue every 100ms
        else:
            self.btn_live.setChecked(False)
            self.btn_sim.setChecked(True)
            self.queue_timer.stop()

            # Standalone simulates running processes as active
            self.led_a.set_color("#10B981")
            self.led_b.set_color("#10B981")
            self.led_c.set_color("#10B981")
            self.led_d.set_color("#10B981")

            self.status_bar.showMessage("SIMULATION MODE: Generating random smart traffic data every 2 seconds...")
            self.run_simulation_step()  # Initial immediate run
            self.sim_timer.start(2000)  # Step every 2 seconds

    # ----------------------------------------------------
    # CORE RECURRING DATA PRODUCERS
    # ----------------------------------------------------

    def run_simulation_step(self):
        """Generates random data locally matching Node C structures."""
        # 1. Simulate Node A: Raw Traffic Counts
        raw_traffic = {
            "lane1": random.randint(0, 30),
            "lane2": random.randint(0, 30),
            "lane3": random.randint(0, 30),
            "lane4": random.randint(0, 30),
        }

        # 2. Simulate Node B: Analyze density levels
        def get_density(v):
            if v < 5: return "LOW"
            elif v < 15: return "MEDIUM"
            return "HIGH"

        # 3. Simulate Node C: Determine green lights
        def get_green_time(d):
            if d == "HIGH": return 30
            elif d == "MEDIUM": return 20
            return 10

        sim_final_data = {}
        for lane, count in raw_traffic.items():
            density = get_density(count)
            sim_final_data[lane] = {
                "vehicles": count,
                "density": density,
                "green_time": get_green_time(density)
            }

        # Trigger workflow visualization
        self.start_pipeline_animation(sim_final_data)

    def check_queue_step(self):
        """Polls Node C's multiprocessing queue for incoming messages."""
        if self.queue_in is not None:
            try:
                # Non-blocking lookup to preserve GUI thread safety
                data = self.queue_in.get_nowait()
                self.status_bar.showMessage(f"Received package from Live IPC Queue at {time.strftime('%H:%M:%S')}")
                self.start_pipeline_animation(data)
            except Empty:
                pass
        else:
            self.status_bar.showMessage("LIVE QUEUE MODE error: Multiprocessing Queue is unavailable.")

    # ----------------------------------------------------
    # PIPELINE ANIMATION & GRAPHICS ENGINE
    # ----------------------------------------------------

    def start_pipeline_animation(self, final_data):
        """Resets diagram state and fires the frame flow sequence."""
        self.anim_timer.stop()
        self.anim_data = final_data
        self.anim_step = 0
        # Fast animation interval (~150ms per node step)
        self.anim_timer.start(150)

    def on_anim_timer_tick(self):
        """Draws dynamic sequential highlight filters on diagrams."""
        # Reset elements to default stylesheet colors
        self.node_a_box.set_state(active=False)
        self.arrow_1.setStyleSheet("color: #475569; font-size: 12px;")
        self.q1_box.set_state(active=False)
        self.arrow_2.setStyleSheet("color: #475569; font-size: 12px;")
        self.node_b_box.set_state(active=False)
        self.arrow_3.setStyleSheet("color: #475569; font-size: 12px;")
        self.q2_box.set_state(active=False)
        self.arrow_4.setStyleSheet("color: #475569; font-size: 12px;")
        self.node_c_box.set_state(active=False)
        self.arrow_5.setStyleSheet("color: #475569; font-size: 12px;")
        self.q3_box.set_state(active=False)
        self.arrow_6.setStyleSheet("color: #475569; font-size: 12px;")
        self.node_d_box.set_state(active=False)

        # Flashes active LEDs and boxes in order
        if self.anim_step == 0:
            self.node_a_box.set_state(active=True)
            self.led_a.set_color("#06B6D4")  # Flash bright cyan LED during send
        elif self.anim_step == 1:
            self.arrow_1.setStyleSheet("color: #06B6D4; font-size: 12px; font-weight: bold;")
            self.q1_box.set_state(active=True)
        elif self.anim_step == 2:
            self.node_b_box.set_state(active=True)
            self.led_b.set_color("#06B6D4")
        elif self.anim_step == 3:
            self.arrow_3.setStyleSheet("color: #06B6D4; font-size: 12px; font-weight: bold;")
            self.q2_box.set_state(active=True)
        elif self.anim_step == 4:
            self.node_c_box.set_state(active=True)
            self.led_c.set_color("#06B6D4")
        elif self.anim_step == 5:
            self.arrow_5.setStyleSheet("color: #06B6D4; font-size: 12px; font-weight: bold;")
            self.q3_box.set_state(active=True)
        elif self.anim_step == 6:
            self.node_d_box.set_state(active=True)
            self.led_d.set_color("#06B6D4")
            # Apply changes to widgets right when animation flow reaches Dashboard Node
            self.apply_ui_update(self.anim_data)
        elif self.anim_step >= 7:
            # End sequence, return indicators to stable active-ready green
            self.anim_timer.stop()
            self.led_a.set_color("#10B981")
            self.led_b.set_color("#10B981")
            self.led_c.set_color("#10B981")
            self.led_d.set_color("#10B981")
            return

        self.anim_step += 1

    # ----------------------------------------------------
    # UPDATE UI DATA
    # ----------------------------------------------------

    def apply_ui_update(self, data):
        """Pushes data records to cards, graphs, and statistics."""
        if not data:
            return

        # 1. Update Lane Cards
        for lane, card in self.cards.items():
            lane_data = data.get(lane, {})
            vehicles = lane_data.get("vehicles", 0)
            density = lane_data.get("density", "LOW")
            green_time = lane_data.get("green_time", 10)
            card.update_data(vehicles, density, green_time)

        # 2. Update Matplotlib Chart
        self.realtime_chart.update_chart(data)

        # 3. Compute System Statistics
        total_vehicles = sum(data[lane].get("vehicles", 0) for lane in data)
        
        # Calculate Average Density (mapped from vehicle numbers)
        avg_vehicles = total_vehicles / 4.0
        if avg_vehicles < 5:
            avg_density = "LOW"
            density_color = "#10B981"
        elif avg_vehicles < 15:
            avg_density = "MEDIUM"
            density_color = "#F59E0B"
        else:
            avg_density = "HIGH"
            density_color = "#EF4444"

        # Determine Active prioritized lane (highest vehicles/green allocation)
        max_lane = max(data, key=lambda k: data[k].get("vehicles", 0))
        active_lane_name = max_lane.replace("lane", "Lane ")
        active_green_time = data[max_lane].get("green_time", 10)

        # Update stats text fields
        self.stat_total_vehicles.value_label.setText(str(total_vehicles))
        self.stat_avg_density.value_label.setText(avg_density)
        self.stat_avg_density.value_label.setStyleSheet(f"color: {density_color}; font-size: 14px; font-weight: bold;")
        self.stat_active_lane.value_label.setText(active_lane_name)
        self.stat_green_time.value_label.setText(f"{active_green_time} sec")

        # 4. Compute Traffic Analytics
        # Peak Traffic Lane
        self.lbl_peak_lane.setText(active_lane_name)

        # Average Vehicles
        avg_vehicles_val = total_vehicles / 4.0
        self.lbl_avg_vehicles.setText(f"{avg_vehicles_val:.1f}")

        # Highest Density Lane (Lane currently classified as HIGH with largest vehicle count)
        high_density_lanes = [l for l in data if data[l].get("density") == "HIGH"]
        if high_density_lanes:
            max_high_lane = max(high_density_lanes, key=lambda k: data[k].get("vehicles", 0))
            highest_density_name = max_high_lane.replace("lane", "Lane ")
        else:
            highest_density_name = "None"
        self.lbl_highest_density_lane.setText(highest_density_name)

        # System Throughput (rolling average packets/sec in last 10s)
        now = time.time()
        self.update_timestamps.append(now)
        self.update_timestamps = [t for t in self.update_timestamps if now - t <= 10.0]
        throughput = len(self.update_timestamps) / 10.0
        self.lbl_throughput.setText(f"{throughput:.2f} packets/sec")

        # 5. Write to CSV Log asynchronously
        self.write_logs_to_csv(data)

    def write_logs_to_csv(self, data):
        """Asynchronously writes traffic data to CSV log file."""
        from datetime import datetime

        def do_write():
            try:
                # Create logs directory if missing
                os.makedirs("logs", exist_ok=True)
                csv_path = os.path.join("logs", "traffic_log.csv")
                file_exists = os.path.isfile(csv_path)

                with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["timestamp", "lane", "vehicles", "density", "green_time"])

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for lane in ["lane1", "lane2", "lane3", "lane4"]:
                        lane_data = data.get(lane, {})
                        vehicles = lane_data.get("vehicles", 0)
                        density = lane_data.get("density", "LOW")
                        green_time = lane_data.get("green_time", 10)
                        writer.writerow([timestamp, lane, vehicles, density, green_time])
            except Exception as e:
                print(f"[CSV LOGGING ERROR]: {e}")

        # Execute in background daemon thread
        threading.Thread(target=do_write, daemon=True).start()

    # ----------------------------------------------------
    # PARALLEL COMPUTING BENCHMARK RUNNER
    # ----------------------------------------------------

    def trigger_benchmark_check(self):
        """Spawns a background thread to run the parallel benchmark."""
        if self.benchmark_running:
            return
        self.benchmark_running = True
        self.status_bar.showMessage("Running Parallel Performance Benchmark in background thread...")

        def thread_target():
            try:
                from benchmark.performance_test import run_benchmark
                # Executes the extended run_benchmark which returns a dict
                metrics = run_benchmark()
                # Safely execute GUI updates on the main thread via singleShot QTimer
                QTimer.singleShot(0, lambda: self.apply_benchmark_metrics(metrics))
            except Exception as e:
                print(f"[BENCHMARK ERROR]: {e}")
                # Reset state on failure
                QTimer.singleShot(0, lambda: setattr(self, "benchmark_running", False))

        # Start daemon thread so it terminates if GUI closes
        t = threading.Thread(target=thread_target, daemon=True)
        t.start()

    def apply_benchmark_metrics(self, metrics):
        """Updates the performance benchmark UI card with fresh metrics."""
        self.benchmark_running = False
        if not metrics:
            return

        seq_time = metrics.get("sequential_time", 0.0)
        par_time = metrics.get("parallel_time", 0.0)
        speedup = metrics.get("speedup", 1.0)
        efficiency = metrics.get("efficiency", 0.0)
        workers = metrics.get("workers", 4)

        self.lbl_seq_time.setText(f"{seq_time:.3f} sec")
        self.lbl_par_time.setText(f"{par_time:.3f} sec")
        self.lbl_workers.setText(str(workers))

        # Speedup visual coloring
        # > 2.5x = Green, 1.5x–2.5x = Yellow, < 1.5x = Red
        self.lbl_speedup.setText(f"{speedup:.2f}x")
        if speedup > 2.5:
            self.lbl_speedup.setStyleSheet("color: #10B981; font-size: 11px; font-weight: bold;")
        elif speedup >= 1.5:
            self.lbl_speedup.setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_speedup.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")

        # Efficiency visual coloring
        # > 70% = Green, 50%-70% = Yellow, < 50% = Red
        self.lbl_efficiency.setText(f"{efficiency:.1f}%")
        if efficiency > 70.0:
            self.lbl_efficiency.setStyleSheet("color: #10B981; font-size: 11px; font-weight: bold;")
        elif efficiency >= 50.0:
            self.lbl_efficiency.setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_efficiency.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: bold;")

        self.status_bar.showMessage(f"Parallel Performance Benchmark updated. Speedup: {speedup:.2f}x.")


# ----------------------------------------------------
# SYSTEM BOOTSTRAP CLASS
# ----------------------------------------------------

class DashboardApp:
    """Wrapper class facilitating integration with parent modules."""
    def __init__(self, queue_in=None):
        self.queue_in = queue_in
        self.app = None
        self.window = None

    def run(self):
        # Prevent starting multiple QApplication context hooks
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            # Apply clean dark color palette styling across native widgets
            self.app.setStyle("Fusion")
            
        self.window = DashboardWindow(queue_in=self.queue_in)
        self.window.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # If run as standalone, boot GUI in SIMULATION mode
    app = DashboardApp()
    app.run()
