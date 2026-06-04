import time

def detect_vehicle(lane_data):
    """Simulates computer vision / vehicle detection algorithm.
    Takes a tuple (lane_name, vehicle_count) and simulates heavy processing.
    Each detection takes 0.5 seconds.
    """
    time.sleep(0.5)
    return lane_data[1]
