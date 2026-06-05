const taskForm = document.getElementById('taskForm');
const taskNameInput = document.getElementById('taskName');
const taskTimeInput = document.getElementById('taskTime');
const taskPriorityInput = document.getElementById('taskPriority');
const taskList = document.getElementById('taskList');
const processorCountInput = document.getElementById('processorCount');
const processorCountValue = document.getElementById('processorCountValue');
const processorLanes = document.getElementById('processorLanes');
const assignTasksButton = document.getElementById('assignTasks');
const runSimulationButton = document.getElementById('runSimulation');
const resetSimulationButton = document.getElementById('resetSimulation');
const exportResultsButton = document.getElementById('exportResults');
const sampleDataButton = document.getElementById('sampleData');
const clearTasksButton = document.getElementById('clearTasks');
const themeToggle = document.getElementById('themeToggle');
const toast = document.getElementById('toast');
const updateTime = document.getElementById('updateTime');
const cardTotalTasks = document.getElementById('cardTotalTasks');
const cardTotalProcessors = document.getElementById('cardTotalProcessors');
const cardSpeedup = document.getElementById('cardSpeedup');
const cardUtilization = document.getElementById('cardUtilization');
const heroTotalTasks = document.getElementById('heroTotalTasks');
const heroProcessors = document.getElementById('heroProcessors');
const heroSpeedup = document.getElementById('heroSpeedup');
const heroEfficiency = document.getElementById('heroEfficiency');
const summarySequentialTime = document.getElementById('summarySequentialTime');
const summaryParallelTime = document.getElementById('summaryParallelTime');
const summaryEfficiency = document.getElementById('summaryEfficiency');
const simSequentialTime = document.getElementById('simSequentialTime');
const simParallelTime = document.getElementById('simParallelTime');
const simEfficiency = document.getElementById('simEfficiency');
const activeLanesCount = document.getElementById('activeLanesCount');
const idleLanesCount = document.getElementById('idleLanesCount');
const loadBalanceScore = document.getElementById('loadBalanceScore');
const ganttChart = document.getElementById('ganttChart');

let tasks = [];
let processorCount = Number(processorCountInput.value);
let schedule = [];
let currentTheme = 'dark';
let charts = {
  distribution: null,
  utilization: null,
  comparison: null,
};

const palette = [
  '#5b8df9', '#34d399', '#f97316', '#fb7185', '#60a5fa', '#f59e0b', '#a855f7', '#22c55e', '#38bdf8', '#f43f5e'
];

function initialize() {
  processorCountValue.textContent = processorCount;
  renderProcessorLanes();
  renderProcessorStatusCards();
  renderTaskList();
  renderMetrics();
  initCharts();
  updateTimestamp();
}

function updateTimestamp() {
  const now = new Date();
  updateTime.textContent = `Last update: ${now.toLocaleString()}`;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2600);
}

function exportResults() {
  const exportData = {
    generatedAt: new Date().toISOString(),
    taskCount: tasks.length,
    processorCount,
    tasks,
    schedule,
    metrics: {
      sequentialTime: simSequentialTime ? simSequentialTime.textContent : '0 ms',
      parallelTime: simParallelTime ? simParallelTime.textContent : '0 ms',
      efficiency: simEfficiency ? simEfficiency.textContent : '0%',
      speedup: cardSpeedup.textContent,
      utilization: cardUtilization.textContent,
    },
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const downloadLink = document.createElement('a');
  downloadLink.href = URL.createObjectURL(blob);
  downloadLink.download = 'parallel-simulation-results.json';
  downloadLink.click();
  URL.revokeObjectURL(downloadLink.href);
  showToast('Simulation results exported successfully.');
}

function createSampleTasks() {
  schedule = [];
  tasks = [
    { id: crypto.randomUUID(), name: 'Load Data', duration: 130, priority: 'High' },
    { id: crypto.randomUUID(), name: 'Process Batch', duration: 90, priority: 'Medium' },
    { id: crypto.randomUUID(), name: 'Analyze Output', duration: 120, priority: 'High' },
    { id: crypto.randomUUID(), name: 'Sync Results', duration: 60, priority: 'Low' },
    { id: crypto.randomUUID(), name: 'Render Graphs', duration: 100, priority: 'Medium' },
  ];

  renderTaskList();
  updateCharts();
  updateTimestamp();
  showToast('Sample task set loaded. Assign tasks to begin simulation.');
}

function renderTaskList() {
  cardTotalTasks.textContent = tasks.length;
  if (!tasks.length) {
    taskList.classList.add('empty-state');
    taskList.innerHTML = `<p>No tasks available. Add a task to begin scheduling.</p>`;
    return;
  }

  taskList.classList.remove('empty-state');
  taskList.innerHTML = tasks
    .map((task) => {
      return `
        <div class="task-item">
          <div>
            <strong>${task.name}</strong>
            <div class="task-meta">${task.duration} ms • Priority: ${task.priority}</div>
          </div>
          <div class="task-actions">
            <button class="btn btn-secondary" onclick="editTask('${task.id}')" title="Edit task">✎</button>
            <button class="btn btn-secondary" onclick="deleteTask('${task.id}')" title="Remove task">✕</button>
          </div>
        </div>
      `;
    })
    .join('');
}

function renderProcessorLanes() {
  cardTotalProcessors.textContent = processorCount;
  processorLanes.innerHTML = '';
  for (let i = 1; i <= processorCount; i += 1) {
    const lane = document.createElement('div');
    lane.className = 'processor-lane';
    lane.innerHTML = `
      <div>Processor ${i}</div>
      <span>Idle</span>
    `;
    processorLanes.appendChild(lane);
  }
}

function renderGantt() {
  if (!schedule.length) {
    ganttChart.classList.add('empty-state');
    ganttChart.innerHTML = `<p>Assign tasks and run the simulation to generate the timeline view.</p>`;
    return;
  }

  ganttChart.classList.remove('empty-state');
  ganttChart.innerHTML = schedule
    .map((processor) => {
      const totalTime = processor.parallelTime || processor.tasks.reduce((sum, item) => sum + item.duration, 0) || 1;
      const stream = processor.tasks
        .map((task) => {
          const start = (task.start / totalTime) * 100;
          const width = (task.duration / totalTime) * 100;
          const color = task.color;
          return `<div class="gantt-block" style="left: ${start}%; width: ${width}%; background: ${color};">${task.name}</div>`;
        })
        .join('');

      return `
        <div class="gantt-row">
          <div class="gantt-label">P${processor.id}</div>
          <div class="gantt-track" style="position: relative;">
            ${stream}
          </div>
        </div>
      `;
    })
    .join('');
}

function renderMetrics() {
  const sequentialTime = tasks.reduce((sum, task) => sum + task.duration, 0);
  const parallelTime = schedule.length
    ? Math.max(...schedule.map((processor) => processor.finishTime))
    : 0;
  const speedup = parallelTime > 0 ? sequentialTime / parallelTime : 0;
  const efficiency = processorCount > 0 && speedup > 0 ? (speedup / processorCount) * 100 : 0;
  const totalBusy = schedule.reduce((sum, processor) => sum + processor.finishTime, 0);
  const utilization = processorCount * parallelTime > 0 ? (totalBusy / (processorCount * parallelTime)) * 100 : 0;

  heroTotalTasks && (heroTotalTasks.textContent = tasks.length);
  heroProcessors && (heroProcessors.textContent = processorCount);
  heroSpeedup && (heroSpeedup.textContent = `${speedup.toFixed(2)}x`);
  heroEfficiency && (heroEfficiency.textContent = `${efficiency.toFixed(1)}%`);

  summarySequentialTime && (summarySequentialTime.textContent = `${sequentialTime} ms`);
  summaryParallelTime && (summaryParallelTime.textContent = parallelTime ? `${parallelTime} ms` : '0 ms');
  summaryEfficiency && (summaryEfficiency.textContent = `${efficiency.toFixed(1)}%`);

  simSequentialTime && (simSequentialTime.textContent = `${sequentialTime} ms`);
  simParallelTime && (simParallelTime.textContent = parallelTime ? `${parallelTime} ms` : '0 ms');
  simEfficiency && (simEfficiency.textContent = `${efficiency.toFixed(1)}%`);

  cardSpeedup.textContent = `${speedup.toFixed(2)}x`;
  cardUtilization.textContent = `${utilization.toFixed(1)}%`;
}

function assignTasks() {
  if (!tasks.length) {
    showToast('Add tasks before assignment.');
    return;
  }

  schedule = [];
  for (let i = 1; i <= processorCount; i += 1) {
    schedule.push({ id: i, tasks: [], currentTime: 0, finishTime: 0, parallelTime: 0 });
  }

  const sortedTasks = [...tasks].sort((a, b) => {
    const priorityOrder = { High: 1, Medium: 2, Low: 3 };
    if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    }
    return b.duration - a.duration;
  });

  sortedTasks.forEach((task, index) => {
    const earliest = schedule.reduce((min, processor) => {
      if (processor.currentTime < min.currentTime) return processor;
      return min;
    });
    earliest.tasks.push({
      ...task,
      start: earliest.currentTime,
      color: palette[index % palette.length],
    });
    earliest.currentTime += task.duration;
    earliest.finishTime = earliest.currentTime;
  });

  const maxFinish = Math.max(...schedule.map((processor) => processor.finishTime));
  schedule.forEach((processor) => {
    processor.parallelTime = maxFinish || 0;
  });

  renderGantt();
  renderProcessorStatus();
  renderMetrics();
  updateCharts();
  showToast('Tasks assigned to processors successfully.');
}

function renderProcessorStatus() {
  const lanes = processorLanes.querySelectorAll('.processor-lane');
  schedule.forEach((processor, index) => {
    const statusText = processor.tasks.length ? `Busy • ${processor.finishTime} ms` : 'Idle';
    if (lanes[index]) {
      lanes[index].querySelector('span').textContent = statusText;
    }
  });
  renderProcessorStatusCards();
}

function renderProcessorStatusCards() {
  const active = schedule.filter((processor) => processor.tasks.length).length;
  const idle = processorCount - active;
  const balance = processorCount > 0 ? Math.round((active / processorCount) * 100) : 0;

  activeLanesCount && (activeLanesCount.textContent = active);
  idleLanesCount && (idleLanesCount.textContent = idle);
  loadBalanceScore && (loadBalanceScore.textContent = `${balance}%`);
}

function runSimulation() {
  if (!schedule.length) {
    showToast('Assign tasks before running simulation.');
    return;
  }

  const bars = ganttChart.querySelectorAll('.gantt-block');
  bars.forEach((bar) => {
    bar.style.opacity = '0';
    bar.style.transition = 'none';
    const delay = parseFloat(bar.style.left) * 0.01 * 0.6;
    setTimeout(() => {
      bar.style.transition = 'all 0.8s ease';
      bar.style.opacity = '1';
      bar.style.transform = 'translateY(-2px)';
    }, delay * 1000);
  });

  showToast('Simulation is animating the parallel schedule.');
}

function resetSimulation() {
  schedule = [];
  renderGantt();
  renderProcessorStatus();
  renderMetrics();
  showToast('Simulation reset. Tasks remain available for reassignment.');
}

function updateCharts() {
  const priorityCounts = tasks.reduce(
    (acc, task) => {
      acc[task.priority] += 1;
      return acc;
    },
    { High: 0, Medium: 0, Low: 0 }
  );

  const utilizationValues = schedule.map((processor) => processor.finishTime);
  const executionComparison = {
    sequential: tasks.reduce((sum, task) => sum + task.duration, 0),
    parallel: schedule.length ? Math.max(...schedule.map((processor) => processor.finishTime)) : 0,
  };

  if (charts.distribution) {
    charts.distribution.data.datasets[0].data = [priorityCounts.High, priorityCounts.Medium, priorityCounts.Low];
    charts.distribution.update();
  }

  if (charts.utilization) {
    charts.utilization.data.labels = schedule.map((processor) => `P${processor.id}`);
    charts.utilization.data.datasets[0].data = utilizationValues;
    charts.utilization.update();
  }

  if (charts.comparison) {
    charts.comparison.data.datasets[0].data = [executionComparison.sequential, executionComparison.parallel];
    charts.comparison.update();
  }
}

function initCharts() {
  const distributionCtx = document.getElementById('taskDistributionChart').getContext('2d');
  const utilizationCtx = document.getElementById('utilizationChart').getContext('2d');
  const comparisonCtx = document.getElementById('comparisonChart').getContext('2d');

  charts.distribution = new Chart(distributionCtx, {
    type: 'doughnut',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ['#fb7185', '#60a5fa', '#34d399'],
        borderWidth: 0,
      }],
    },
    options: { plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1' } } } },
  });

  charts.utilization = new Chart(utilizationCtx, {
    type: 'bar',
    data: {
      labels: Array.from({ length: processorCount }, (_, i) => `P${i + 1}`),
      datasets: [{
        label: 'Busy Time (ms)',
        data: Array.from({ length: processorCount }, () => 0),
        backgroundColor: '#76d6ff',
        borderRadius: 12,
        maxBarThickness: 40,
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
        y: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' }}
      },
    },
  });

  charts.comparison = new Chart(comparisonCtx, {
    type: 'line',
    data: {
      labels: ['Sequential', 'Parallel'],
      datasets: [{
        label: 'Execution Time (ms)',
        data: [0, 0],
        borderColor: '#3cc4ff',
        backgroundColor: 'rgba(60, 196, 255, 0.16)',
        tension: 0.35,
        fill: true,
        pointRadius: 6,
        pointBackgroundColor: '#7dd3fc',
      }],
    },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
        y: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } },
      },
    },
  });
}

function addTask(event) {
  event.preventDefault();
  const name = taskNameInput.value.trim();
  const duration = Number(taskTimeInput.value);
  const priority = taskPriorityInput.value;

  if (!name || duration <= 0) {
    showToast('Please enter a valid task name and execution duration.');
    return;
  }

  const task = {
    id: crypto.randomUUID(),
    name,
    duration,
    priority,
  };

  tasks.push(task);
  taskForm.reset();
  renderTaskList();
  updateCharts();
  updateTimestamp();
  showToast('Task added successfully.');
}

function editTask(taskId) {
  const task = tasks.find((item) => item.id === taskId);
  if (!task) return;

  taskNameInput.value = task.name;
  taskTimeInput.value = task.duration;
  taskPriorityInput.value = task.priority;
  deleteTask(taskId, false);
  showToast('Edit the task and submit to update it.');
}

function deleteTask(taskId, notify = true) {
  tasks = tasks.filter((task) => task.id !== taskId);
  renderTaskList();
  if (notify) showToast('Task deleted successfully.');
  updateCharts();
}

function clearAllTasks() {
  tasks = [];
  schedule = [];
  renderTaskList();
  renderGantt();
  renderProcessorStatus();
  renderMetrics();
  updateCharts();
  showToast('All tasks cleared.');
}

function toggleTheme() {
  const body = document.body;
  if (currentTheme === 'dark') {
    body.classList.remove('theme-dark');
    body.classList.add('theme-light');
    themeToggle.textContent = 'Dark Mode';
    currentTheme = 'light';
    showToast('Light theme activated.');
  } else {
    body.classList.remove('theme-light');
    body.classList.add('theme-dark');
    themeToggle.textContent = 'Light Mode';
    currentTheme = 'dark';
    showToast('Dark theme activated.');
  }
}

function handleProcessorCountChange() {
  processorCount = Number(processorCountInput.value);
  processorCountValue.textContent = processorCount;
  renderProcessorLanes();
  assignTasks();
}

window.editTask = editTask;
window.deleteTask = deleteTask;

taskForm.addEventListener('submit', addTask);
clearTasksButton.addEventListener('click', clearAllTasks);
sampleDataButton.addEventListener('click', createSampleTasks);
exportResultsButton.addEventListener('click', exportResults);
processorCountInput.addEventListener('input', handleProcessorCountChange);
assignTasksButton.addEventListener('click', assignTasks);
runSimulationButton.addEventListener('click', runSimulation);
resetSimulationButton.addEventListener('click', resetSimulation);
themeToggle.addEventListener('click', toggleTheme);

initialize();
