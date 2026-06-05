# System Architecture

The system consists of three independent monitoring nodes:

1. Heart Rate Node
2. Temperature Node
3. Oxygen Saturation Node

Each node executes as a separate process.

All monitoring data are displayed concurrently through the central console.

Parallel processing is implemented using Python Multiprocessing.
