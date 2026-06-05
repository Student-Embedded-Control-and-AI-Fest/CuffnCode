"""
=============================================================
Pemrosesan Banyak Gambar Lebih Cepat dengan Komputasi Paralel
=============================================================
Program ini membandingkan pemrosesan gambar secara sequential
dan parallel menggunakan Python multiprocessing.
"""

import os
import time
import cv2
from multiprocessing import Pool, cpu_count


# ==================== KONFIGURASI ====================

FOLDER_INPUT = "images"
FOLDER_OUTPUT_SEQ = "output_sequential"
FOLDER_OUTPUT_PAR = "output_parallel"
UKURAN_GAMBAR = (500, 500)  # Ukuran resize gambar

# Nonaktifkan multi-threading internal OpenCV
# agar perbandingan sequential vs parallel lebih akurat
cv2.setNumThreads(1)


# ==================== FUNGSI UTILITAS ====================

def buat_folder(path):
    """Membuat folder jika belum ada."""
    if not os.path.exists(path):
        os.makedirs(path)


def ambil_daftar_gambar(folder):
    """Mengambil daftar file gambar dari folder input."""
    ekstensi_valid = (".jpg", ".jpeg", ".png")
    daftar = []
    for nama_file in os.listdir(folder):
        if nama_file.lower().endswith(ekstensi_valid):
            daftar.append(nama_file)
    return sorted(daftar)


# ==================== FUNGSI PROSES GAMBAR ====================

def proses_gambar(args):
    """
    Memproses satu gambar dengan tahapan berat:
    1. Resize gambar ke ukuran besar (simulasi resolusi tinggi)
    2. Ubah ke grayscale
    3. Beri efek blur berulang kali (simulasi proses berat)
    4. Deteksi tepi (edge detection)
    5. Resize akhir ke 500x500
    6. Simpan ke folder output
    """
    path_input, path_output = args

    # Baca gambar dari file
    gambar = cv2.imread(path_input)
    if gambar is None:
        print(f"  [GAGAL] Tidak bisa membaca: {path_input}")
        return

    # Langkah 1: Resize gambar ke ukuran besar (simulasi gambar resolusi tinggi)
    gambar = cv2.resize(gambar, (2500, 2500))

    # Langkah 2: Ubah ke grayscale
    gambar = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)

    # Langkah 3: Beri efek blur berulang kali (proses berat untuk simulasi)
    for _ in range(20):
        gambar = cv2.GaussianBlur(gambar, (21, 21), 0)

    # Langkah 4: Deteksi tepi menggunakan Canny
    tepi = cv2.Canny(gambar, 50, 150)

    # Gabungkan hasil blur dan edge detection
    gambar = cv2.addWeighted(gambar, 0.7, tepi, 0.3, 0)

    # Langkah 5: Resize akhir ke ukuran output
    gambar = cv2.resize(gambar, UKURAN_GAMBAR)

    # Langkah 6: Simpan hasil ke folder output
    cv2.imwrite(path_output, gambar)


# ==================== METODE SEQUENTIAL ====================

def proses_sequential(daftar_gambar):
    """Memproses semua gambar satu per satu (sequential)."""
    print("\n[1] Memulai pemrosesan SEQUENTIAL...")
    print(f"    Memproses {len(daftar_gambar)} gambar satu per satu.\n")

    # Siapkan folder output
    buat_folder(FOLDER_OUTPUT_SEQ)

    # Siapkan daftar tugas (input, output)
    tugas = []
    for nama in daftar_gambar:
        path_in = os.path.join(FOLDER_INPUT, nama)
        path_out = os.path.join(FOLDER_OUTPUT_SEQ, nama)
        tugas.append((path_in, path_out))

    # Catat waktu mulai
    waktu_mulai = time.time()

    # Proses gambar satu per satu
    for i, t in enumerate(tugas, 1):
        proses_gambar(t)
        print(f"    [{i}/{len(tugas)}] Selesai: {t[0]}")

    # Catat waktu selesai
    waktu_selesai = time.time()
    durasi = waktu_selesai - waktu_mulai

    print(f"\n    Pemrosesan sequential selesai dalam {durasi:.4f} detik.")
    return durasi


# ==================== METODE PARALLEL ====================

def proses_parallel(daftar_gambar):
    """Memproses semua gambar secara bersamaan (parallel)."""
    jumlah_proses = cpu_count()
    print(f"\n[2] Memulai pemrosesan PARALLEL...")
    print(f"    Memproses {len(daftar_gambar)} gambar dengan {jumlah_proses} proses.\n")

    # Siapkan folder output
    buat_folder(FOLDER_OUTPUT_PAR)

    # Siapkan daftar tugas (input, output)
    tugas = []
    for nama in daftar_gambar:
        path_in = os.path.join(FOLDER_INPUT, nama)
        path_out = os.path.join(FOLDER_OUTPUT_PAR, nama)
        tugas.append((path_in, path_out))

    # Catat waktu mulai
    waktu_mulai = time.time()

    # Proses gambar secara parallel menggunakan Pool
    with Pool(processes=jumlah_proses) as pool:
        pool.map(proses_gambar, tugas)

    # Catat waktu selesai
    waktu_selesai = time.time()
    durasi = waktu_selesai - waktu_mulai

    print(f"    Pemrosesan parallel selesai dalam {durasi:.4f} detik.")
    return durasi


# ==================== TAMPILKAN HASIL ====================

def tampilkan_hasil(jumlah, waktu_seq, waktu_par):
    """Menampilkan perbandingan hasil di terminal."""
    selisih = waktu_seq - waktu_par
    if waktu_par > 0:
        speedup = waktu_seq / waktu_par
    else:
        speedup = 0

    if waktu_seq < waktu_par:
        lebih_cepat = "Sequential"
    else:
        lebih_cepat = "Parallel"

    print("\n" + "=" * 55)
    print("        HASIL PERBANDINGAN WAKTU PROSES")
    print("=" * 55)
    print(f"  Jumlah gambar diproses  : {jumlah} gambar")
    print(f"  Waktu sequential        : {waktu_seq:.4f} detik")
    print(f"  Waktu parallel          : {waktu_par:.4f} detik")
    print(f"  Selisih waktu           : {abs(selisih):.4f} detik")
    print(f"  Speedup                 : {speedup:.2f}x")
    print(f"  Metode lebih cepat      : {lebih_cepat}")
    print("=" * 55)
    print(f"\n  Kesimpulan: Metode {lebih_cepat} lebih cepat")
    print(f"  dengan selisih {abs(selisih):.4f} detik.\n")


# ==================== PROGRAM UTAMA ====================

if __name__ == "__main__":
    print("=" * 55)
    print(" PEMROSESAN BANYAK GAMBAR DENGAN KOMPUTASI PARALEL")
    print("=" * 55)

    # Cek apakah folder images ada
    if not os.path.exists(FOLDER_INPUT):
        print(f"\n[ERROR] Folder '{FOLDER_INPUT}' tidak ditemukan!")
        print(f"Silakan buat folder '{FOLDER_INPUT}' dan isi dengan gambar.")
        print("Format yang didukung: .jpg, .jpeg, .png")
        exit(1)

    # Ambil daftar gambar
    daftar_gambar = ambil_daftar_gambar(FOLDER_INPUT)

    # Cek apakah ada gambar di folder
    if len(daftar_gambar) == 0:
        print(f"\n[ERROR] Tidak ada gambar di folder '{FOLDER_INPUT}'!")
        print("Silakan masukkan gambar ke folder tersebut.")
        print("Format yang didukung: .jpg, .jpeg, .png")
        exit(1)

    print(f"\nDitemukan {len(daftar_gambar)} gambar di folder '{FOLDER_INPUT}'.")

    # Jalankan pemrosesan sequential
    waktu_seq = proses_sequential(daftar_gambar)

    # Jalankan pemrosesan parallel
    waktu_par = proses_parallel(daftar_gambar)

    # Tampilkan hasil perbandingan
    tampilkan_hasil(len(daftar_gambar), waktu_seq, waktu_par)
