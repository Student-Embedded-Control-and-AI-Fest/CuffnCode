from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

rooms = []
devices = []
history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add-room", methods=["POST"])
def add_room():
    room = request.json["room"]
    if room and room not in rooms:
        rooms.append(room)
    return jsonify(success=True)

@app.route("/delete-room", methods=["POST"])
def delete_room():
    room = request.json["room"]
    global devices
    # Menghapus device yang ada di dalam room tersebut
    devices = [d for d in devices if d["room"] != room]
    if room in rooms:
        rooms.remove(room)
    return jsonify(success=True)

@app.route("/add-device", methods=["POST"])
def add_device():
    devices.append({
        "name": request.json["name"],
        "watt": int(request.json["watt"]),
        "room": request.json["room"],
        "active": False
    })
    return jsonify(success=True)

@app.route("/edit-device", methods=["POST"])
def edit_device():
    index = int(request.json["index"])
    if 0 <= index < len(devices):
        devices[index]["name"] = request.json["name"]
        devices[index]["watt"] = int(request.json["watt"])
        devices[index]["room"] = request.json["room"]
    return jsonify(success=True)

@app.route("/delete-device", methods=["POST"])
def delete_device():
    index = int(request.json["index"])
    if 0 <= index < len(devices):
        devices.pop(index)
    return jsonify(success=True)

@app.route("/toggle-device", methods=["POST"])
def toggle_device():
    index = int(request.json["index"])
    
    if 0 <= index < len(devices):
        device = devices[index]
        
        # Jika perangkat saat ini MATI dan user ingin menyalakannya
        if not device["active"]:
            room_name = device["room"]
            # Hitung total watt perangkat yang SEDANG MENYALA di ruangan yang sama
            current_room_watt = sum(d["watt"] for d in devices if d["room"] == room_name and d["active"])
            
            # Jika ditambah perangkat ini melebihi 1000W, tolak!
            if current_room_watt + device["watt"] > 1000:
                return jsonify({
                    "success": False, 
                    "message": f"Overload! Kapasitas maksimal {room_name} adalah 1000W. Sisa kapasitas tidak cukup untuk menyalakan perangkat ini."
                })
                
        # Jika lolos validasi (atau jika user mematikan perangkat), ubah statusnya
        devices[index]["active"] = not devices[index]["active"]
        return jsonify({"success": True})
        
    return jsonify({"success": False, "message": "Device tidak ditemukan"})


@app.route("/monitor")
def monitor():
    room_usage = {room: 0 for room in rooms}
    total_power = 0
    active_devices = 0
    top_device = "-"
    top_watt = 0

    for device in devices:
        if device["active"]:
            active_devices += 1
            total_power += device["watt"]
            room_usage[device["room"]] += device["watt"]
            
        if device["watt"] > top_watt:
            top_watt = device["watt"]
            top_device = device["name"]

    highest_room = max(room_usage, key=room_usage.get) if room_usage else "-"

    if total_power < 300: efficiency = 100
    elif total_power < 500: efficiency = 80
    elif total_power < 700: efficiency = 60
    else: efficiency = 40

    recommendation = "Normal"
    if total_power > 500: recommendation = "High Energy Usage"
    if total_power > 1000: recommendation = "Critical Energy Usage"

    room_status = {}
    for room, watt in room_usage.items():
        if watt < 300: room_status[room] = "NORMAL"
        elif watt < 700: room_status[room] = "HIGH"
        else: room_status[room] = "CRITICAL"

    history.append(total_power)
    if len(history) > 20: history.pop(0)

    return jsonify({
        "rooms": rooms,
        "devices": devices,
        "room_usage": room_usage,
        "room_status": room_status,
        "total_power": total_power,
        "active_devices": active_devices,
        "total_rooms": len(rooms),
        "highest_room": highest_room,
        "efficiency": efficiency,
        "recommendation": recommendation,
        "top_device": top_device,
        "top_watt": top_watt,
        "history": history
    })

if __name__ == "__main__":
    app.run(debug=True)