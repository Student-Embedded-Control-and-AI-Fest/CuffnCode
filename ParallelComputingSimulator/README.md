# Parallel Computing Visualization Simulator

![Project Status](https://img.shields.io/badge/Status-Ready%20for%20Submission-success?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-HTML%20%7C%20CSS%20%7C%20JavaScript%20%7C%20Chart.js-informational?style=for-the-badge)

## Overview

The Parallel Computing Visualization Simulator is a browser-based tool developed for university-level coursework in parallel computing. It provides an interactive interface for creating tasks, configuring processor counts, assigning workloads, and analyzing scheduling performance through charts and Gantt visualizations.

## Key Capabilities

- Add, edit, and remove computation tasks with execution time and priority.
- Configure processor count dynamically from 1 to 8 cores.
- Assign tasks across processors using a greedy load-balancing scheduler.
- Display a Gantt chart that visualizes task execution across processor lanes.
- Calculate and compare sequential vs. parallel runtime metrics.
- Export simulation results to a JSON report.
- Load sample task sets for fast demonstration and testing.
- View analytics charts for priority distribution, processor utilization, and execution comparisons.

## Academic Relevance

This simulator is intended to reinforce core parallel computing concepts:

- Task scheduling and workload balancing.
- Processor utilization and idle time analysis.
- Speedup and efficiency evaluation.
- The difference between sequential and parallel execution models.
- Visual interpretation of scheduling outcomes in a Gantt chart.

## Technology Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js

## Project Structure

```
ParallelComputingSimulator/
├── index.html
├── style.css
├── script.js
├── README.md
├── assets/
│   ├── screenshots/
│   ├── icons/
│   └── images/
└── docs/
    └── project-documentation.md
```

## Running the Application

1. Clone or download the repository.
2. Open the folder containing the project files.
3. Open `index.html` in a modern browser.

No build process or server is required.

## Usage Instructions

1. Use the Task Manager to enter a task name, execution time, and priority.
2. Click **Add Task** to insert the task into the queue.
3. Adjust the processor slider to select the number of processors.
4. Click **Assign Tasks** to distribute tasks across processor lanes.
5. Click **Run Simulation** to animate the Gantt chart.
6. Click **Export Results** to save the current simulation state as JSON.
7. Use **Load Sample Tasks** to populate the simulator with example workloads.

## Metrics Explained

- **Sequential Execution Time**: The sum of all task durations if executed one after another.
- **Parallel Execution Time**: The time taken by the slowest processor after scheduling.
- **Speedup**: The ratio of sequential runtime to parallel runtime.
- **Efficiency**: Speedup normalized by the number of processors.
- **Utilization**: The proportion of processor capacity used during execution.

## Notes for Submission

- Designed for university coursework in parallel computing.
- Fully client-side implementation compatible with GitHub Pages.
- Includes UI/UX improvements for accessibility and academic presentation.
- Contains a dedicated educational section explaining relevant concepts.

## Suggested Extensions

- Add configurable scheduling policies (e.g. round robin, earliest deadline first).
- Add dependency graph support and communication delays.
- Store task sets in browser storage for persistent sessions.
- Provide export options for charts and visual reports.

## Author

- Student name: [Your Name]
- Course: Parallel Computing
- Institution: [Your University]
- Submission type: Academic project

## License

MIT License
