def allocate_green_time(density):

    if density == "HIGH":
        return 30

    elif density == "MEDIUM":
        return 20

    else:
        return 10


def controller_node(queue_in, queue_out):

    print("[NODE C] Started")

    analysis_data = queue_in.get()

    final_data = {}

    for lane, data in analysis_data.items():

        final_data[lane] = {
            "vehicles":
                data["vehicles"],

            "density":
                data["density"],

            "green_time":
                allocate_green_time(
                    data["density"]
                )
        }

    queue_out.put(final_data)

    print("[NODE C] Decision Complete")