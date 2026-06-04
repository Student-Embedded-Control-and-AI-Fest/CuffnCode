def classify_density(vehicle_count):

    if vehicle_count < 5:
        return "LOW"

    elif vehicle_count < 15:
        return "MEDIUM"

    else:
        return "HIGH"


def analysis_node(queue_in, queue_out):

    print("[NODE B] Started")

    traffic_data = queue_in.get()

    result = {}

    for lane, vehicles in traffic_data.items():

        result[lane] = {
            "vehicles": vehicles,
            "density": classify_density(
                vehicles
            )
        }

    queue_out.put(result)

    print("[NODE B] Analysis Complete")