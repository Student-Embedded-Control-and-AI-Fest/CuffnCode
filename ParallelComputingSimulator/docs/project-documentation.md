# Parallel Computing Visualization Simulator: Academic Project Report

## Abstract

This report documents the development and evaluation of a browser-based Parallel Computing Visualization Simulator. The application is designed to support undergraduate instruction in parallel computing by presenting task scheduling, processor load balancing, and performance metrics through an interactive dashboard. The simulator integrates a Gantt chart visualization, configurable processor settings, and analytics rendered with Chart.js. The objective is to provide a pedagogical tool that translates theoretical scheduling concepts into an intuitive, hands-on experience.

## Introduction

Parallel computing is a central topic in computer science curricula and is critical for improving performance in modern computing systems. Students often encounter difficulty in conceptualizing how tasks are scheduled across multiple processors and how these decisions influence execution time. The Parallel Computing Visualization Simulator addresses this gap by offering an accessible, browser-based interface that visualizes parallel schedules, metrics, and processor utilization.

## Background

In sequential execution, tasks are processed one after another on a single processor. This approach may lead to long completion times and underutilization of available hardware resources. Parallel computing mitigates these issues by distributing independent tasks across multiple processors, allowing concurrent execution. Effective scheduling is necessary to minimize idle time and maximize throughput. Visualization tools make these abstract concepts more concrete by demonstrating task assignment, processor activity, and the relationship between sequential and parallel runtimes.

## Problem Statement

The principal problem addressed by this project is the absence of a simple, browser-based educational simulator that illustrates the fundamentals of parallel task scheduling and performance evaluation. Existing resources often require installation, focus on theoretical concepts without visual support, or do not provide real-time comparison between sequential and parallel execution. This project aims to create a lightweight educational platform that demonstrates key parallel computing concepts without requiring server-side infrastructure.

## Objectives

The project objectives are as follows:

- Develop a polished and responsive dashboard suitable for academic demonstration.
- Implement task lifecycle management including task creation, editing, deletion, and clearing.
- Enable dynamic configuration of processor count from one to eight processors.
- Assign tasks using a scheduling algorithm and visualize the schedule with a Gantt chart.
- Compute and display core performance metrics such as speedup, efficiency, and processor utilization.
- Provide analytic charts for priority distribution, processor utilization, and execution comparison.
- Support sample task loading and export of simulation results for academic reporting.

## Literature Review

A range of educational tools and scholarly works have examined methods for teaching parallel computing. Hennessy and Patterson (2019) emphasize workload distribution and processor efficiency as essential aspects of computer architecture. Grama et al. (2003) describe the pedagogical value of visual aids in presenting scheduling strategies and parallel algorithms. Prior research suggests that interactive simulations can enhance comprehension by allowing students to observe the effects of scheduling decisions in real time. The use of Gantt chart visualizations is also well established for illustrating task allocation and processor utilization in both project management and computer science education.

## Methodology

The project was implemented using HTML5, CSS3, and vanilla JavaScript. Chart.js was integrated to render analytics charts and support responsive graphical output. The development methodology comprised the following activities:

1. Define the functional requirements for a parallel computing educational simulator.
2. Design a clear and accessible user interface with semantic structure and responsive layout.
3. Implement a task management system that supports add, edit, delete, and clear operations.
4. Develop a scheduling engine that assigns tasks to processors based on current load and priority.
5. Render a Gantt chart to visualize processor lanes and task execution timelines.
6. Compute performance metrics and update visualizations in real time.
7. Validate the system with sample workloads and interaction scenarios.

## System Design

The system architecture is organized into modular components that reflect distinct functional concerns:

- **Task Management:** Manages task entry, validation, update, deletion, and persistence within the browser session.
- **Processor Configuration:** Enables selection of processor count and displays processor status updates.
- **Scheduling Engine:** Allocates tasks to processors using a greedy load-balancing strategy and computes start and finish times.
- **Visualization Module:** Produces the Gantt chart and updates analytic visualizations rendered with Chart.js.
- **Metrics Module:** Calculates sequential time, parallel time, speedup, efficiency, and processor utilization.
- **Export Module:** Generates a downloadable JSON file containing the task set, schedule, and performance metrics.

The interface uses a sidebar navigation pattern, cards for metric display, and a responsive grid layout to support both desktop and mobile use.

## Scheduling Algorithm

The scheduling algorithm implemented in this project is a greedy load-balancing algorithm. The algorithm follows these steps:

1. Sort tasks by priority, with High priority tasks first, followed by Medium and Low.
2. Within each priority level, sort tasks by descending execution time to promote balanced allocation.
3. For each task, select the processor with the lowest current accumulated load.
4. Assign the task to that processor and update the processor's current time and finish time.
5. Use the maximum finish time across all processors as the parallel execution time.

This scheduling strategy approximates efficient workload distribution by always selecting the least-loaded processor at assignment time. It is suitable for educational purposes because it demonstrates how priority and processor load influence scheduling outcomes.

## Parallel Computing Concepts

The simulator reinforces several foundational parallel computing concepts:

- **Task Scheduling:** The process of determining which processors execute which tasks and when.
- **Workload Balancing:** The distribution of tasks across processors to minimize idle time and maximize efficiency.
- **Processor Lanes:** Each processor is represented as an execution lane in the Gantt chart.
- **Sequential vs Parallel Execution:** Sequential execution processes tasks one after another, while parallel execution distributes tasks among processors concurrently.
- **Priority Scheduling:** Tasks with higher priority are scheduled before tasks with lower priority, affecting the order in which tasks are executed.

## Performance Metrics

The simulator computes several performance metrics to assess scheduling effectiveness:

- **Sequential Execution Time:** The sum of all task durations. This represents the runtime if tasks were processed serially on a single processor.
- **Parallel Execution Time:** The maximum processor finish time after scheduling. This is the elapsed time for parallel execution.
- **Speedup:** Computed as the ratio of sequential execution time to parallel execution time. Speedup indicates how much the parallel schedule improves performance over serial execution.
- **Efficiency:** Calculated as speedup divided by the number of processors, expressed as a percentage. Efficiency measures the effective use of processor resources.
- **Processor Utilization:** The percentage of total processor capacity that is actively used during the schedule. It represents the ratio of busy processor time to total available processor time.

## User Interface Design

The user interface is designed to support academic exploration through clarity and responsiveness. Key design features include:

- Sidebar navigation with links to Dashboard, Task Manager, Processor Configuration, Simulation, Analytics, and Educational Reference sections.
- A task input form with validation for name, execution time, and priority.
- Processor slider control for selecting between one and eight processors.
- Action buttons for loading sample tasks, assigning tasks, running simulation animations, resetting the schedule, and exporting results.
- Metric cards that display sequential time, parallel time, speedup, efficiency, and utilization.
- A Gantt chart view that visually represents task execution across processor lanes.
- Chart.js analytics for task priority distribution, processor utilization, and execution comparison.
- Responsive layout optimized for desktop, tablet, and mobile displays.

## Testing and Validation

The application was validated using a combination of manual interaction tests and scenario evaluations:

- Form validation checks ensured that tasks require a non-empty name and a positive execution time.
- Task lifecycle operations were tested by adding, editing, deleting, and clearing tasks.
- Processor configuration was tested by changing the processor count and reassigning tasks.
- Sample task loading was verified to ensure quick demonstration and reproducibility.
- Export functionality was validated by generating JSON files and examining exported data structure.
- Analytics charts were verified to update correctly after task assignment and schedule changes.
- Gantt chart rendering was inspected to confirm accurate task alignment and lane allocation.
- Responsive behavior was tested across various viewport widths.

## Results and Discussion

The simulator successfully demonstrated key effects of parallel execution. When the processor count increases, the parallel execution time generally decreases, yielding improved speedup. Efficiency and processor utilization metrics reveal how effectively the available processing resources are used.

The sample tasks feature provides a convenient baseline for classroom demonstration and enables students to compare scheduling results quickly. Exporting results supports evidence-based reporting by preserving the task set, schedule, and computed metrics in a portable format.

The visualization components help make scheduling tradeoffs more transparent. For example, the Gantt chart clearly shows how tasks are assigned to different processor lanes and where idle time occurs. The analytics charts further contextualize priority distribution and utilization patterns.

## Advantages and Limitations

Advantages:

- The application is fully client-side and does not require server deployment.
- The interface is designed for educational clarity and usability.
- Real-time metrics and visualizations support active learning.
- Export and sample-loading capabilities enhance academic use.

Limitations:

- The scheduler uses a heuristic greedy algorithm and does not guarantee optimal results for all task sets.
- The current model does not incorporate task dependencies or communication overhead.
- The visualization normalizes scheduling timelines based on the longest processor load, which may simplify detailed timing behavior.
- The simulator is intended for instructional use rather than production scheduling.

## Future Improvements

Future enhancements could include:

- Additional scheduling strategies such as round robin, earliest deadline first, and work stealing.
- Support for task dependency graphs and precedence constraints.
- Modeling of communication latency and synchronization costs.
- Persistent browser storage for task sets and configuration state.
- Export options for chart images or formatted PDF reports.

## Workflow Description

The simulator workflow is straightforward and supports iterative exploration:

1. Enter task details and add tasks to the Task Manager.
2. Adjust the processor count using the slider.
3. Click **Assign Tasks** to distribute tasks to processors.
4. Review the Gantt chart, processor status, and performance metrics.
5. Optionally click **Run Simulation** to animate the schedule.
6. Export the simulation results to a JSON file for reporting.

This workflow enables students to explore how different schedules and processor configurations affect parallel performance.

## Conclusion

The Parallel Computing Visualization Simulator provides an effective educational platform for illustrating parallel computing concepts. It combines task scheduling, processor configuration, Gantt chart visualization, and performance metrics in a cohesive browser-based interface. The application is well suited for university coursework, allowing students to explore the relationships between sequential runtime, parallel runtime, speedup, efficiency, and processor utilization.

## References

- Hennessy, J. L., & Patterson, D. A. (2019). *Computer Architecture: A Quantitative Approach*. Morgan Kaufmann.
- Grama, A., Gupta, A., Karypis, G., & Kumar, V. (2003). *Introduction to Parallel Computing*. Addison-Wesley.
- Chart.js. (2026). *Chart.js Documentation*. Retrieved from https://www.chartjs.org/
- World Wide Web Consortium. (2018). *HTML5 Specification*.
- World Wide Web Consortium. (2018). *CSS3 Specification*.
