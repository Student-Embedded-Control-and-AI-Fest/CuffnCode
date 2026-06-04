def dashboard_node(queue_in):

    print("[NODE D] Started")

    result = queue_in.get()

    print("\n")
    print("=" * 50)
    print("SMART TRAFFIC DASHBOARD")
    print("=" * 50)

    for lane, data in result.items():

        print()

        print(
            f"Lane      : {lane}"
        )

        print(
            f"Vehicles  : {data['vehicles']}"
        )

        print(
            f"Density   : {data['density']}"
        )

        print(
            f"GreenTime : {data['green_time']} sec"
        )

    print()
    print("=" * 50)