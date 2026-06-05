import threading
import time

PIN_PUMP = 1          
PIN_SOLENOID_1 = 2      
PIN_SOLENOID_2 = 3       

current_pressure = 0     
is_running = True         

mock_pump_state = 0
mock_sol1_state = 0
mock_sol2_state = 0

TARGET_PRESSURE = 150 

def digital_write_sim(pin, state):
    global mock_pump_state, mock_sol1_state, mock_sol2_state
    if pin == PIN_PUMP:
        mock_pump_state = state
    elif pin == PIN_SOLENOID_1:
        mock_sol1_state = state
    elif pin == PIN_SOLENOID_2:
        mock_sol2_state = state

def task_read_sensor():
    global current_pressure, is_running
    while is_running:
        if current_pressure < TARGET_PRESSURE and mock_pump_state == 1:
            current_pressure += 10  
        elif mock_sol2_state == 1:
            current_pressure -= 15  
        
        if current_pressure < 0:
            current_pressure = 0

        print(f"[THREAD SENSOR] Tekanan Saat Ini: {current_pressure} mmHg")
        
        time.sleep(0.1)

def task_system_control():
    global is_running
    print("\n[THREAD KONTROL] Mula-mula: Menutup Katup Buang & Menyalakan Pompa...\n")
    
    digital_write_sim(PIN_SOLENOID_2, 0) 
    digital_write_sim(PIN_SOLENOID_1, 1) 
    digital_write_sim(PIN_PUMP, 1)       
    
    while is_running:
        if current_pressure >= TARGET_PRESSURE:
            print("\n[THREAD KONTROL] >> TARGET TERCAPAI! <<")
            print("[THREAD KONTROL] Mematikan Pompa & Mengunci Tekanan (Solenoid 1 OFF).\n")
            
            digital_write_sim(PIN_PUMP, 0)   
            digital_write_sim(PIN_SOLENOID_1, 0) 
            
            time.sleep(3) 
            
            print("\n[THREAD KONTROL] Proses Selesai. Membuka Katup Solenoid 2 ke Atmosfer...\n")
            digital_write_sim(PIN_SOLENOID_2, 1) 
            
            time.sleep(2) 
            
            is_running = False  
        
        time.sleep(0.2)

if __name__ == "__main__":
    print("==================================================")
    print("      CUFFNCODE PARALLEL COMPUTING (PYTHON)       ")
    print("==================================================")
    
    thread_sensor = threading.Thread(target=task_read_sensor)
    thread_control = threading.Thread(target=task_system_control)
    
    thread_sensor.start()
    thread_control.start()
    
    thread_sensor.join()
    thread_control.join()

    print("==================================================")
    print("       SISTEM SELESAI DENGAN AMAN DAN PARALEL       ")
    print("==================================================")
