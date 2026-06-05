import multiprocessing
import time
import random
import os

def sensor_node(queue):
    """Node 1: Simulasi Sensor Kamera di Jalan (Akuisisi Data)"""
    while True:
        lajur_utara = random.randint(5, 50)
        lajur_selatan = random.randint(5, 50)
        
        queue.put({'Lajur Utara': lajur_utara, 'Lajur Selatan': lajur_selatan})
        time.sleep(2) 

def controller_node(queue):
    """Node 2: Pusat Kontrol & Dashboard Terminal (Analisis Data)"""
    while True:
        if not queue.empty():
            data = queue.get()
             
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("="*45)
            print(" 🚦 SMART TRAFFIC DASHBOARD (LITE V1.0) 🚦")
            print("="*45)
            
            for lajur, jumlah in data.items():
                if jumlah > 35:
                    kepadatan = "TINGGI (MACET)  🔴"
                    lampu_hijau = "45 Detik"
                elif jumlah > 15:
                    kepadatan = "SEDANG          🟡"
                    lampu_hijau = "25 Detik"
                else:
                    kepadatan = "RENDAH (LANCAR) 🟢"
                    lampu_hijau = "10 Detik"
                
                print(f"📍 {lajur}")
                print(f"   🚗 Jumlah Kendaraan : {jumlah} unit")
                print(f"   📊 Status Kepadatan : {kepadatan}")
                print(f"   🚥 Durasi Lampu Hijau: {lampu_hijau}\n")
            
            print("="*45)
            print("Sistem berjalan paralel... Menunggu data sensor...")
        time.sleep(0.1)

if __name__ == '__main__':
    multiprocessing.freeze_support() 
    print("Memulai Sistem Smart Traffic Terdistribusi...")

    ipc_queue = multiprocessing.Queue()

    p_sensor = multiprocessing.Process(target=sensor_node, args=(ipc_queue,))
    p_control = multiprocessing.Process(target=controller_node, args=(ipc_queue,))
    
    p_sensor.start()
    p_control.start()
    
    try:
        p_sensor.join()
        p_control.join()
    except KeyboardInterrupt:
        print("\nMematikan sistem secara aman...")
        p_sensor.terminate()
        p_control.terminate()