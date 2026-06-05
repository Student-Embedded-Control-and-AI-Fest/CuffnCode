import threading
import time
import random

kapasitas = 10
kendaraan_parkir = []
lock = threading.Lock()

def gerbang_masuk(nama_gerbang):
    global kendaraan_parkir

    for i in range(3):
        time.sleep(random.randint(1, 3))

        with lock:
            if len(kendaraan_parkir) < kapasitas:
                plat = f"{nama_gerbang}-{i+1}"
                kendaraan_parkir.append(plat)

                print(f"[{nama_gerbang}] Kendaraan {plat} MASUK")
                print(f"Total kendaraan: {len(kendaraan_parkir)}")
            else:
                print(f"[{nama_gerbang}] Parkiran penuh")

def gerbang_keluar():
    global kendaraan_parkir

    for i in range(3):
        time.sleep(random.randint(2, 4))

        with lock:
            if kendaraan_parkir:
                plat = kendaraan_parkir.pop(0)

                print(f"[GERBANG KELUAR] Kendaraan {plat} KELUAR")
                print(f"Total kendaraan: {len(kendaraan_parkir)}")
            else:
                print("[GERBANG KELUAR] Tidak ada kendaraan")

# Membuat thread
masuk1 = threading.Thread(target=gerbang_masuk, args=("Gerbang 1",))
masuk2 = threading.Thread(target=gerbang_masuk, args=("Gerbang 2",))
keluar = threading.Thread(target=gerbang_keluar)

# Menjalankan thread
masuk1.start()
masuk2.start()
keluar.start()

# Menunggu semua selesai
masuk1.join()
masuk2.join()
keluar.join()

print("\n=== SIMULASI SELESAI ===")
print("Kendaraan yang masih parkir:")
for kendaraan in kendaraan_parkir:
    print("-", kendaraan)

print(f"Slot tersisa: {kapasitas - len(kendaraan_parkir)}")