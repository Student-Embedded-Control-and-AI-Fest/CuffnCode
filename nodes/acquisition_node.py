from simulator.traffic_generator import generate_traffic
import time


def acquisition_node(queue_out):

    print("[NODE A] Started")

    traffic_data = generate_traffic()

    time.sleep(1)

    queue_out.put(traffic_data)

    print("[NODE A] Traffic Sent")