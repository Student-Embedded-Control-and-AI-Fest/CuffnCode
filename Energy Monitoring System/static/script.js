let chart = null;
let editingDeviceIndex = null; 

function addRoom() {
    const room = document.getElementById("roomName").value.trim();
    if (room === "") { alert("Room name required"); return; }
    fetch("/add-room", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ room })
    })
    .then(r => r.json())
    .then(() => {
        document.getElementById("roomName").value = "";
        loadData();
    });
}

function deleteRoom(roomName) {
    if(confirm(`Yakin ingin menghapus room "${roomName}" dan semua perangkat di dalamnya?`)){
        fetch("/delete-room", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ room: roomName })
        })
        .then(r => r.json())
        .then(() => loadData());
    }
}

function addDevice() {
    const name = document.getElementById("deviceName").value.trim();
    const watt = document.getElementById("deviceWatt").value;
    const room = document.getElementById("deviceRoom").value;
    if (name === "" || watt === "" || room === "") { alert("Fill all fields"); return; }

    // Jika mode edit
    if (editingDeviceIndex !== null) {
        fetch("/edit-device", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ index: editingDeviceIndex, name, watt, room })
        })
        .then(r => r.json())
        .then(() => {
            resetDeviceForm();
            loadData();
        });
    } else {
        // Jika mode tambah baru
        fetch("/add-device", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, watt, room })
        })
        .then(r => r.json())
        .then(() => {
            resetDeviceForm();
            loadData();
        });
    }
}

function editDevice(index) {
    fetch("/monitor")
    .then(r => r.json())
    .then(data => {
        const device = data.devices[index];
        document.getElementById("deviceName").value = device.name;
        document.getElementById("deviceWatt").value = device.watt;
        document.getElementById("deviceRoom").value = device.room;
        
        editingDeviceIndex = index;
        document.getElementById("btnSubmitDevice").innerText = "Update";
        document.getElementById("btnSubmitDevice").classList.add("btn-update");
    });
}

function resetDeviceForm() {
    document.getElementById("deviceName").value = "";
    document.getElementById("deviceWatt").value = "";
    editingDeviceIndex = null;
    const btn = document.getElementById("btnSubmitDevice");
    btn.innerText = "Tambahkan";
    btn.classList.remove("btn-update");
}

function toggleDevice(index) {
    fetch("/toggle-device", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index })
    })
    .then(r => r.json())
    .then(res => {
        // Jika gagal karena melebihi kapasitas 1000W, tampilkan pesan error
        if (!res.success) {
            alert(res.message);
        }
        // Pastikan loadData dipanggil agar checkbox kembali ke state aslinya jika gagal
        loadData();
    });
}

function deleteDevice(index) {
    fetch("/delete-device", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index })
    })
    .then(r => r.json())
    .then(() => loadData());
}

function updateChart(history) {
    const ctx = document.getElementById("powerChart");
    if (chart) { chart.destroy(); }
    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: history.map((_, i) => i + 1),
            datasets: [{
                label: "Building Load (W)",
                data: history,
                borderColor: "#00b050",
                backgroundColor: "rgba(0,176,80,0.08)",
                tension: 0.4,
                pointBackgroundColor: "#00b050",
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, labels: { color: "#333", font: { family: "'Poppins', sans-serif", size: 12 } } }
            },
            scales: {
                x: { ticks: { color: "#888" }, grid: { color: "#e8f5ec" } },
                y: { ticks: { color: "#888" }, grid: { color: "#e8f5ec" } }
            }
        }
    });
}

function loadData() {
    fetch("/monitor")
    .then(r => r.json())
    .then(data => {
        // Stats
        document.getElementById("totalPower").innerText = data.total_power + " W";
        document.getElementById("totalRooms").innerText = data.total_rooms;
        document.getElementById("activeDevices").innerText = data.active_devices;
        document.getElementById("efficiency").innerText = data.efficiency + "%";

        // Top device & room
        document.getElementById("topDevice").innerText = data.top_device + " (" + data.top_watt + "W)";
        document.getElementById("highestRoom").innerText = data.highest_room;

        // Recommendation
        const recEl = document.getElementById("recommendation");
        recEl.innerText = data.recommendation;
        recEl.className = "";
        if (data.total_power > 1000) recEl.classList.add("critical");
        else if (data.total_power > 500) recEl.classList.add("warn");

        // Room select dropdown
        const roomSelect = document.getElementById("deviceRoom");
        const prev = roomSelect.value;
        roomSelect.innerHTML = "";
        data.rooms.forEach(room => {
            const opt = document.createElement("option");
            opt.value = room;
            opt.textContent = room;
            roomSelect.appendChild(opt);
        });
        if (prev && data.rooms.includes(prev)) roomSelect.value = prev;

        // Device table
        const tbody = document.getElementById("deviceTableBody");
        if (data.devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#aaa;padding:12px;">Belum ada device</td></tr>';
        } else {
            tbody.innerHTML = "";
            data.devices.forEach((device, index) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><span class="room-label">${device.room}</span></td>
                    <td>${device.name}</td>
                    <td>${device.watt} W</td>
                    <td>
                        <input type="checkbox" ${device.active ? "checked" : ""} onchange="toggleDevice(${index})">
                    </td>
                    <td>
                        <button class="edit-btn" onclick="editDevice(${index})">Edit</button>
                        <button class="del-btn" onclick="deleteDevice(${index})">Hapus</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Room monitoring table
        const roomUsage = document.getElementById("roomUsage");
        roomUsage.innerHTML = "";
        for (const room in data.room_usage) {
            const watt = data.room_usage[room];
            const status = data.room_status[room];
            let statusClass = "status-normal";
            if (status === "HIGH") statusClass = "status-high";
            if (status === "CRITICAL") statusClass = "status-critical";
            
            // Kolom dengan tombol hapus room
            roomUsage.innerHTML += `
                <tr>
                    <td>${room}</td>
                    <td>Total : ${watt} W</td>
                    <td class="${statusClass}">Status : ${status}</td>
                    <td style="text-align: right;">
                        <button class="del-btn" onclick="deleteRoom('${room}')">Hapus</button>
                    </td>
                </tr>
            `;
        }
        updateChart(data.history);
    });
}

loadData();
setInterval(() => {
    // Hindari reset dropdown & form saat user sedang ngetik/edit
    if(editingDeviceIndex === null) {
        loadData();
    }
}, 3000);