import time
from simulator.building_generator import generate_energy_data


def collection_worker(output_queue):

    while True:

        data = generate_energy_data()

        print("[COLLECTION]", data)

        output_queue.put(data)

        time.sleep(1)