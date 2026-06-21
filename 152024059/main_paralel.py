import os
import time
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageOps

INPUT_DIR = "input_images"
OUTPUT_DIR = "output_images"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_single_image(img_name):
    try:
        img_path = os.path.join(INPUT_DIR, img_name)
        img = Image.open(img_path)
        gray_img = ImageOps.grayscale(img)
        resized_img = gray_img.resize((800, 800))
        resized_img.save(os.path.join(OUTPUT_DIR, img_name))
    except Exception as e:
        print(f"Error proses {img_name}: {e}")

def run_serial(images):
    start = time.time()
    for img in images:
        process_single_image(img)
    return time.time() - start

def run_parallel(images):
    start = time.time()
    with ProcessPoolExecutor() as executor:
        executor.map(process_single_image, images)
    return time.time() - start

if __name__ == "__main__":
    if os.path.exists(INPUT_DIR):
        images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    else:
        images = []
    
    if not images:
        print(f"Folder '{INPUT_DIR}' belum ada atau kosong! Pastikan kamu sudah membuat folder tersebut dan mengisinya dengan gambar hasil copy-paste manual.")
    else:
        print(f"Menemukan {len(images)} gambar. Memulai pengujian performa...\n")

        print("Mengeksekusi proses SERIAL...")
        time_serial = run_serial(images)
        print(f"Selesai! Waktu Serial: {time_serial:.2f} detik\n")
        print("Mengeksekusi proses PARALEL...")
        time_parallel = run_parallel(images)
        print(f"Selesai! Waktu Paralel: {time_parallel:.2f} detik\n")
        
        speedup = time_serial / time_parallel
        print("==================================================")
        print(f"Peningkatan Kecepatan (Speedup): {speedup:.2f}x lebih cepat!")
        print("==================================================")
