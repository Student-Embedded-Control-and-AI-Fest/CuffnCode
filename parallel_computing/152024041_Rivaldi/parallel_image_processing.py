

# ==============================================================================
# IMPORT LIBRARIES
# ==============================================================================
import os
import time
from pathlib import Path

from PIL import Image, ImageFilter

# concurrent.futures adalah modul bawaan Python (std library) yang menyediakan
# antarmuka tingkat tinggi untuk menjalankan tugas secara asynchronous.
# ProcessPoolExecutor adalah implementasi yang menggunakan proses (bukan thread)
# sehingga cocok untuk tugas CPU-bound seperti image processing.
from concurrent.futures import ProcessPoolExecutor, as_completed


# ==============================================================================
# KONSTANTA FOLDER
# ==============================================================================
# Path relatif terhadap lokasi script ini dijalankan.
# Menggunakan Pathlib agar cross-platform (Windows/Linux/macOS).

FOLDER_INPUT = Path("images")           # Folder berisi gambar mentah (.jpg/.png)
FOLDER_SEKUENSIAL = Path("hasil_sekuensial")  # Output hasil pemrosesan sequential
FOLDER_PARALEL = Path("hasil_paralel")        # Output hasil pemrosesan parallel

# Filter yang akan diterapkan pada setiap gambar
FILTER_YANG_DIGUNAKAN = ImageFilter.BLUR


# ==============================================================================
# FUNGSI INTI: memproses SATU gambar
# ==============================================================================
def proses_satu_gambar(nama_file: str) -> str:
    """
    Memproses SATU gambar:
      1. Membaca file dari folder 'images/'
      2. Konversi ke grayscale (mode 'L')
      3. Terapkan filter blur
      4. Simpan ke folder 'hasil_sekuensial/' dan 'hasil_paralel/'

    Parameter:
        nama_file (str): Nama file gambar (misal: 'foto1.jpg')

    Returns:
        str: Nama file yang berhasil diproses (untuk logging)

    —— PENJELASAN ——
    Fungsi ini adalah "unit kerja" terkecil dalam program.
    Baik proses sekuensial maupun paralel akan memanggil fungsi yang SAMA
    untuk memproses setiap gambar. Tidak ada modifikasi kode — hanya cara
    pemanggilannya yang berbeda.

    Ini penting untuk memastikan perbandingan waktu yang adil (apple-to-apple).
    """
    path_input = FOLDER_INPUT / nama_file

    # Buka gambar asli
    gambar = Image.open(path_input)

    # —— Konversi Grayscale ——
    # Mode 'L' (Luminance) mengubah gambar berwarna menjadi hitam-putih
    # dengan 256 tingkat keabuan (0 = hitam, 255 = putih).
    gambar_grayscale = gambar.convert("L")

    # —— Terapkan Blur ——
    # ImageFilter.BLUR adalah filter low-pass sederhana bawaan PIL
    # yang menghaluskan gambar dengan merata-ratakan piksel tetangga.
    gambar_blur = gambar_grayscale.filter(FILTER_YANG_DIGUNAKAN)

    # —— Simpan ke kedua folder output ——
    # Path output: hasil_sekuensial/<nama_file> dan hasil_paralel/<nama_file>
    path_output_sekuensial = FOLDER_SEKUENSIAL / nama_file
    path_output_paralel = FOLDER_PARALEL / nama_file

    gambar_blur.save(path_output_sekuensial)
    gambar_blur.save(path_output_paralel)

    # Tutup objek gambar untuk membebaskan memory
    gambar.close()

    return nama_file


# ==============================================================================
# EKSEKUSI SEKUENSIAL
# ==============================================================================
def proses_sekuensial(daftar_gambar: list) -> float:
    """
    Memproses gambar SATU PER SATU menggunakan loop for biasa.
    Ini adalah cara tradisional / sequential.

    Parameter:
        daftar_gambar (list): List nama file gambar

    Returns:
        float: Total waktu eksekusi dalam detik
    """
    print("[SEKUENSIAL] Memproses gambar secara berurutan...")
    waktu_mulai = time.perf_counter()  # Mulai stopwatch

    # Loop sederhana: proses gambar satu per satu
    # Setiap iterasi MENUNGGU gambar selesai diproses sebelum lanjut ke
    # gambar berikutnya. Jika ada 10 gambar, waktu total = jumlah waktu
    # masing-masing gambar.
    for gambar in daftar_gambar:
        proses_satu_gambar(gambar)
        print(f"  -> {gambar} selesai")

    waktu_selesai = time.perf_counter()  # Hentikan stopwatch
    total_waktu = waktu_selesai - waktu_mulai

    return total_waktu


# ==============================================================================
# EKSEKUSI PARALEL (dengan ProcessPoolExecutor)
# ==============================================================================
def proses_paralel(daftar_gambar: list) -> float:
    """
    Memproses gambar SECARA BERSAMAAN menggunakan ProcessPoolExecutor.

    —— KENAPA ProcessPoolExecutor BUKAN ThreadPoolExecutor? ——
    Image processing adalah CPU-bound task — tugas yang membutuhkan banyak
    komputasi prosesor (baca piksel, ubah nilai, tulis piksel).
    Python memiliki GIL (Global Interpreter Lock) yang membatasi Thread hanya
    bisa mengeksekusi satu instruksi dalam satu waktu.
    Akibatnya, ThreadPoolExecutor TIDAK akan memberikan speedup signifikan
    untuk CPU-bound task.

    ProcessPoolExecutor membuat beberapa PROSES terpisah (masing-masing punya
    interpreter Python sendiri + memory sendiri), sehingga bisa memanfaatkan
    INTI CPU yang berbeda secara nyata (true parallel execution).

    —— BAGAIMANA BEKERJANYA? ——
    1. ProcessPoolExecutor membuat "worker pool" — sekumpulan proses anak.
       Jumlah worker default = jumlah CPU core di komputer Anda.
    2. Method .map() membagi daftar gambar ke worker-worker tersebut.
    3. Setiap worker memproses gambar dengan fungsi yang kita berikan.
    4. Hasilnya dikumpulkan kembali secara otomatis.

    Analogi:
      Sekuensial -> 1 koki memasak 10 menu satu per satu.
      Paralel    -> 4 koki memasak 10 menu secara bersamaan (masing-masing
                    mengerjakan menu yang berbeda).

    Parameter:
        daftar_gambar (list): List nama file gambar

    Returns:
        float: Total waktu eksekusi dalam detik
    """
    print("[PARALEL] Memproses gambar secara paralel...")
    waktu_mulai = time.perf_counter()  # Mulai stopwatch

    # —— Membuat ProcessPoolExecutor ——
    # with-statement memastikan executor ditutup otomatis setelah selesai.
    # Jika tidak disebutkan, max_workers = jumlah CPU core.
    # Anda bisa menentukan secara eksplisit: ProcessPoolExecutor(max_workers=4)
    with ProcessPoolExecutor() as executor:
        """
        —— PENJELASAN .map() ——
        Method .map() bekerja mirip seperti fungsi map() bawaan Python:
          map(fungsi, iterable) -> memanggil fungsi untuk setiap item

        Bedanya, ProcessPoolExecutor.map() MEMBAGI iterable ke worker-worker
        yang berjalan di proses terpisah, sehingga dieksekusi secara paralel.

        Analogi kode:
            Hasil:  [proses_satu_gambar("a.jpg"),
                     proses_satu_gambar("b.jpg"),
                     proses_satu_gambar("c.jpg")]
        Tapi semua dari mereka bisa jalan BERSAMAAN (paralel), bukan
        satu per satu (sekuensial).

        .map() akan mengembalikan hasil dalam urutan yang sama dengan input.
        """
        # executor.map secara otomatis:
        #   1. Membagi daftar_gambar ke worker-worker
        #   2. Setiap worker memanggil proses_satu_gambar(nama_file)
        #   3. Mengumpulkan semua hasilnya
        hasil = executor.map(proses_satu_gambar, daftar_gambar)

    # Cetak hasil (sudah berurutan sesuai input)
    for nama in hasil:
        print(f"  -> {nama} selesai")

    waktu_selesai = time.perf_counter()  # Hentikan stopwatch
    total_waktu = waktu_selesai - waktu_mulai

    return total_waktu


# ==============================================================================
# FUNGSI UTAMA (entry point)
# ==============================================================================
def main():
    """
    Fungsi utama yang mengatur alur program:

    1. Validasi folder input
    2. Membuat folder output jika belum ada
    3. Membaca daftar gambar yang akan diproses
    4. Menjalankan tes sekuensial
    5. Menjalankan tes paralel
    6. Menampilkan kesimpulan perbandingan
    """
    print("=" * 60)
    print("  PERBANDINGAN SEKUENSIAL vs PARALEL (IMAGE PROCESSING)")
    print("=" * 60)

    # ======================================================================
    # STEP 1: Validasi folder input
    # ======================================================================
    if not FOLDER_INPUT.exists():
        print(f"\n[ERROR] Folder '{FOLDER_INPUT}' tidak ditemukan!")
        print(f"Buat folder '{FOLDER_INPUT}' dan masukkan gambar .jpg/.png ke dalamnya.")
        return

    # ======================================================================
    # STEP 2: Kumpulkan daftar gambar
    # ======================================================================
    # Filter hanya file dengan ekstensi gambar yang umum (.jpg, .jpeg, .png)
    # Menggunakan .suffix untuk mendapatkan ekstensi file.
    ekstensi_diizinkan = {".jpg", ".jpeg", ".png"}
    daftar_gambar = [
        f.name for f in FOLDER_INPUT.iterdir()
        if f.is_file() and f.suffix.lower() in ekstensi_diizinkan
    ]
    daftar_gambar.sort()  # Urutkan agar konsisten antar eksekusi

    if not daftar_gambar:
        print(f"\n[ERROR] Folder '{FOLDER_INPUT}' kosong atau tidak mengandung file gambar!")
        print(f"Pastikan ada file .jpg atau .png di folder '{FOLDER_INPUT}'.")
        return

    print(f"\nDitemukan {len(daftar_gambar)} gambar: {daftar_gambar}")

    # ======================================================================
    # STEP 3: Buat folder output jika belum ada
    # ======================================================================
    # exist_ok=True => tidak error jika folder sudah ada
    FOLDER_SEKUENSIAL.mkdir(parents=True, exist_ok=True)
    FOLDER_PARALEL.mkdir(parents=True, exist_ok=True)

    # ======================================================================
    # STEP 4: Eksekusi Sekuensial
    # ======================================================================
    print("\n" + "-" * 50)
    waktu_sekuensial = proses_sekuensial(daftar_gambar)
    print(f"\nWaktu sekuensial: {waktu_sekuensial:.2f} detik")
    print("-" * 50)

    # ======================================================================
    # STEP 5: Eksekusi Paralel
    # ======================================================================
    print("\n" + "-" * 50)
    waktu_paralel = proses_paralel(daftar_gambar)
    print(f"\nWaktu paralel: {waktu_paralel:.2f} detik")
    print("-" * 50)

    # ======================================================================
    # STEP 6: Hitung speedup dan tampilkan kesimpulan
    # ======================================================================
    # Speedup = waktu_sekuensial / waktu_paralel
    # Jika > 1, paralel lebih cepat. Jika < 1, sekuensial lebih cepat.
    if waktu_paralel > 0:
        speedup = waktu_sekuensial / waktu_paralel
    else:
        speedup = float("inf")

    print("\n" + "=" * 50)
    print("================ KESIMPULAN ================")
    print(f"Waktu Sekuensial : {waktu_sekuensial:.2f} detik")
    print(f"Waktu Paralel    : {waktu_paralel:.2f} detik")
    if speedup > 1:
        print(f"Komputasi Paralel lebih cepat {speedup:.2f}x lipat!")
    elif speedup == 1:
        print("Waktu komputasi seimbang (tidak ada percepatan).")
    else:
        print(f"Komputasi Sekuensial lebih cepat {1/speedup:.2f}x lipat.")
    print("=" * 50)


# ==============================================================================
# GUARD: if __name__ == "__main__"
# ==============================================================================
#
# —— MENGAPA GUARD INI MANDATORY? ——
#
# Saat Python menjalankan script, variabel __name__ akan bernilai "__main__"
# jika script di-run langsung (misal: python script.py).
#
# Namun, ketika ProcessPoolExecutor membuat PROSES ANAK (child process),
# proses anak juga akan meng-import file ini. TANPA guard, proses anak akan
# menjalankan KEMBALI kode di bawah if __name__ == "__main__", termasuk
# pembuatan ProcessPoolExecutor lagi, yang akan membuat proses cucu,
# dan seterusnya TAK TERHINGGA (infinite recursion).
#
# Ini sangat berbahaya di Windows karena Windows tidak memiliki fork()
# seperti Linux/macOS. Windows harus membuat proses baru dengan menjalankan
# ulang interpreter Python, sehingga tanpa guard akan terjadi:
#   - Crash program
#   - Memory overflow
#   - Pembekuan sistem
#
# KESIMPULAN: SELALU gunakan guard ini ketika menggunakan ProcessPoolExecutor
# atau modul multiprocessing lainnya di Python. Ini bukan best practice —
# ini WAJIB hukumnya.
#
# ==============================================================================
if __name__ == "__main__":
    main()
