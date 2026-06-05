async function startSimulation() {
    const tasks = Number(document.getElementById("tasks").value) || 0;
    const workers = Number(document.getElementById("workers").value) || 0;

    document.getElementById("taskCount").innerText = tasks;
    document.getElementById("workerCount").innerText = workers;
    document.getElementById("timeResult").innerText = "Memproses...";
    document.getElementById("speedUp").innerText = "0x";
    document.getElementById("efficiencyCard").innerText = "0%";
    document.getElementById("serialTime").innerText = "0 s";
    document.getElementById("efficiencyAnalysis").innerText = "0%";
    document.getElementById("workerStatus").innerHTML = `<div class="worker-log">Memproses simulasi...</div>`;
    document.getElementById("workerDistribution").innerHTML = `<div class="worker-log">Memproses distribusi...</div>`;

    const progressBar = document.getElementById("progressBar");
    progressBar.style.width = "0%";
    progressBar.innerText = "0%";

    const resultBox = document.getElementById("resultBox");
    resultBox.innerHTML = "<p>Memproses data...</p>";

    const formData = new FormData();
    formData.append("tasks", tasks);
    formData.append("workers", workers);

    const response = await fetch("/simulate", {
        method: "POST",
        body: formData,
    });

    const data = await response.json();

    if (!data.success) {
        resultBox.innerHTML = `<div class="worker-log">Terjadi kesalahan: ${data.error}</div>`;
        return;
    }

    resultBox.innerHTML = "";

    data.results.forEach((log) => {
        resultBox.innerHTML += `
            <div class="worker-log">
                ${log}
            </div>
        `;
    });

    const progress = data.total_tasks > 0 ? Math.min(100, Math.round((data.results.length / data.total_tasks) * 100)) : 0;
    progressBar.style.width = `${progress}%`;
    progressBar.innerText = `${progress}%`;

    document.getElementById("timeResult").innerText = `${data.execution_time} detik`;
    document.getElementById("speedUp").innerText = `${data.speed_up}x`;
    document.getElementById("efficiencyCard").innerText = `${data.efficiency}%`;
    document.getElementById("serialTime").innerText = `${data.serial_time} s`;
    document.getElementById("efficiencyAnalysis").innerText = `${data.efficiency}%`;

    const statusLines = Object.entries(data.worker_distribution).map(
        ([worker, count]) => `<div class="worker-log">${worker}: ${count} tugas</div>`
    );
    document.getElementById("workerStatus").innerHTML = statusLines.join("");

    const distributionLines = Object.entries(data.worker_distribution).map(
        ([worker, count]) => `<div class="worker-log">${worker}: ${count} tugas</div>`
    );
    document.getElementById("workerDistribution").innerHTML = distributionLines.join("");
}
