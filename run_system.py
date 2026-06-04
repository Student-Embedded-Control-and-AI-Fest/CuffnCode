import sys
import time
import multiprocessing
from queue import Empty

# Import the original nodes
from nodes.acquisition_node import acquisition_node
from nodes.analysis_node import analysis_node
from nodes.controller_node import controller_node
from dashboard_gui import DashboardApp

# ----------------------------------------------------
# MULTIPROCESSING TOP-LEVEL LOOP WRAPPERS
# ----------------------------------------------------
# (These must be top-level functions to allow pickling on Windows)

def loop_acquisition(queue_out, stop_event):
    """Wraps Node A (Traffic Acquisition) to run in a continuous loop."""
    print("[NODE A] Loop Wrapper Started")
    while not stop_event.is_set():
        try:
            # Call the user's original acquisition_node which generates traffic,
            # sleeps for 1 second, and puts data into the output queue.
            acquisition_node(queue_out)
            
            # Wait another 1 second to create a stable ~2s traffic generation loop
            # Check the stop event frequently during the sleep
            for _ in range(10):
                if stop_event.is_set():
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[NODE A ERROR]: {e}")
            time.sleep(1)
    print("[NODE A] Loop Wrapper Terminated")


def loop_analysis(queue_in, queue_out, stop_event):
    """Wraps Node B (Traffic Analysis) to run in a continuous loop."""
    print("[NODE B] Loop Wrapper Started")
    while not stop_event.is_set():
        try:
            # Call user's original analysis_node which waits for queue_in (blocks),
            # classifies density, and puts analyzed data into queue_out.
            analysis_node(queue_in, queue_out)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[NODE B ERROR]: {e}")
            time.sleep(0.5)
    print("[NODE B] Loop Wrapper Terminated")


def loop_controller(queue_in, queue_out, stop_event):
    """Wraps Node C (Adaptive Controller) to run in a continuous loop."""
    print("[NODE C] Loop Wrapper Started")
    while not stop_event.is_set():
        try:
            # Call user's original controller_node which waits for queue_in (blocks),
            # calculates green light time, and puts results into queue_out.
            controller_node(queue_in, queue_out)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[NODE C ERROR]: {e}")
            time.sleep(0.5)
    print("[NODE C] Loop Wrapper Terminated")


# ----------------------------------------------------
# PIPELINE LAUNCHER
# ----------------------------------------------------

def main():
    print("=" * 60)
    print("DISTRIBUTED SMART TRAFFIC SYSTEM - CONCURRENT PIPELINE")
    print("=" * 60)
    print("[SYSTEM] Setting up IPC Multiprocessing Queues...")
    
    # Instantiate Queues representing:
    # Q1: Node A -> Node B
    # Q2: Node B -> Node C
    # Q3: Node C -> Node D (Dashboard)
    q1 = multiprocessing.Queue()
    q2 = multiprocessing.Queue()
    q3 = multiprocessing.Queue()

    # Event for coordinated stop
    stop_event = multiprocessing.Event()

    print("[SYSTEM] Initializing background processes...")
    
    p1 = multiprocessing.Process(
        target=loop_acquisition,
        args=(q1, stop_event),
        name="Node_A_Acquisition"
    )
    p2 = multiprocessing.Process(
        target=loop_analysis,
        args=(q1, q2, stop_event),
        name="Node_B_Analysis"
    )
    p3 = multiprocessing.Process(
        target=loop_controller,
        args=(q2, q3, stop_event),
        name="Node_C_Controller"
    )

    print("[SYSTEM] Starting processes...")
    p1.start()
    p2.start()
    p3.start()
    print("[SYSTEM] Background workers started successfully.")

    # Start Node D (GUI Dashboard) on the main thread (Q3 queue reader)
    print("[SYSTEM] Spawning GUI Dashboard (Node D) on Main Thread...")
    try:
        app = DashboardApp(queue_in=q3)
        app.run()
    except KeyboardInterrupt:
        print("\n[SYSTEM] KeyboardInterrupt caught on main thread. Initiating shutdown...")
    finally:
        # Trigger clean exit of child processes
        print("[SYSTEM] Stopping background processes...")
        stop_event.set()
        
        # Give them a moment to stop or terminate directly
        p1.terminate()
        p2.terminate()
        p3.terminate()
        
        # Clean up queue locks
        q1.close()
        q2.close()
        q3.close()
        q1.join_thread()
        q2.join_thread()
        q3.join_thread()

        # Join processes to prevent orphan processes
        p1.join()
        p2.join()
        p3.join()
        
        print("[SYSTEM] All processes terminated. Clean shutdown complete.")
        print("=" * 60)


if __name__ == "__main__":
    # Standard Windows multiprocessing protection
    multiprocessing.freeze_support()
    main()
