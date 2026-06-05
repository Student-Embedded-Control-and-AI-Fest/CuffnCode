# Optimasi Pemrosesan Citra Menggunakan Komputasi Paralel di Python

## Evaluasi 3 - Komputasi Paralel

### Anggota Kelompok

* Bagus Wiguna Herdiansyah - 152024054
---

# Deskripsi Proyek

Proyek ini bertujuan untuk membandingkan performa pemrosesan citra digital menggunakan metode sekuensial dan metode paralel. Studi kasus yang digunakan adalah pengolahan beberapa gambar secara bersamaan dengan menerapkan proses konversi grayscale dan filter blur.

Pada pemrosesan sekuensial, gambar diproses satu per satu secara berurutan. Sebaliknya, pada pemrosesan paralel, pekerjaan dibagi ke beberapa proses yang berjalan secara bersamaan sehingga dapat memanfaatkan beberapa inti prosesor (CPU Core) secara optimal.

Implementasi dilakukan menggunakan bahasa Python dengan memanfaatkan modul `concurrent.futures.ProcessPoolExecutor`.

---

# Latar Belakang

Dalam pengolahan citra digital, jumlah data yang diproses sering kali sangat besar. Ketika jumlah gambar meningkat, waktu pemrosesan menjadi semakin lama jika dilakukan secara sekuensial.

Komputasi paralel memungkinkan beberapa tugas dijalankan secara bersamaan pada beberapa inti prosesor. Dengan pendekatan ini, waktu pemrosesan dapat dipersingkat dan efisiensi sistem dapat ditingkatkan.

---

# Tujuan

1. Memahami konsep komputasi paralel.
2. Membandingkan waktu eksekusi antara metode sekuensial dan paralel.
3. Mengimplementasikan pemrosesan citra menggunakan ProcessPoolExecutor.
4. Mengukur peningkatan performa yang diperoleh melalui komputasi paralel.

---

# Teknologi yang Digunakan

## Hardware

* Processor Multi-Core
* RAM Minimal 4 GB

## Software

* Python 3.x
* Pillow (PIL)
* Concurrent Futures
* Visual Studio Code

---

# Metode Pemrosesan

## Pemrosesan Sekuensial

Pada metode ini, setiap gambar diproses satu per satu menggunakan perulangan biasa (`for loop`).

Alur proses:

1. Membaca gambar.
2. Mengubah gambar menjadi grayscale.
3. Menerapkan filter blur.
4. Menyimpan hasil.
5. Melanjutkan ke gambar berikutnya.

Karena setiap tugas harus selesai terlebih dahulu sebelum tugas berikutnya dimulai, waktu total eksekusi menjadi lebih lama ketika jumlah gambar bertambah.

---

## Pemrosesan Paralel

Pada metode paralel digunakan `ProcessPoolExecutor`.

Alur proses:

1. Membuat beberapa worker process.
2. Membagi daftar gambar ke setiap worker.
3. Setiap worker memproses gambar secara bersamaan.
4. Hasil dikumpulkan kembali setelah seluruh proses selesai.

Metode ini memungkinkan pemanfaatan beberapa CPU Core secara bersamaan sehingga waktu pemrosesan menjadi lebih cepat.

---

# Struktur Folder

```text
Evaluasi_3/
│
├── image_processing.py
│
├── images/
│   ├── gambar1.jpg
│   ├── gambar2.jpg
│   ├── gambar3.jpg
│
├── hasil_sekuensial/
│
└── hasil_paralel/
```

# Cara Menjalankan Program

## Install Dependency

```bash
pip install pillow
```

## Menjalankan Program

```bash
python image_processing.py
```

---

# Hasil Pengujian

Contoh hasil pengujian:

| Metode     | Waktu Eksekusi |
| ---------- | -------------- |
| Sekuensial | 8.50 detik     |
| Paralel    | 3.20 detik     |

Perhitungan speedup:

Speedup = Waktu Sekuensial / Waktu Paralel

Contoh:

```text
Speedup = 8.50 / 3.20
Speedup = 2.65x
```

Artinya komputasi paralel mampu mempercepat proses hingga 2,65 kali dibandingkan metode sekuensial.

---

# Analisis

Berdasarkan hasil pengujian, metode paralel menunjukkan performa yang lebih baik dibandingkan metode sekuensial. Hal ini terjadi karena pekerjaan dibagi ke beberapa proses yang berjalan secara bersamaan pada beberapa inti prosesor.

Semakin banyak data atau gambar yang diproses, semakin besar potensi peningkatan performa yang diperoleh dari komputasi paralel.

---

# Kesimpulan

1. Komputasi paralel dapat meningkatkan efisiensi pemrosesan citra digital.
2. ProcessPoolExecutor mampu memanfaatkan beberapa CPU Core secara bersamaan.
3. Waktu pemrosesan menjadi lebih cepat dibandingkan metode sekuensial.
4. Teknik ini cocok diterapkan pada aplikasi yang membutuhkan pengolahan data dalam jumlah besar.

---

# Referensi

1. Python Documentation – concurrent.futures
2. Python Documentation – multiprocessing
3. Pillow Documentation
4. Materi Perkuliahan Komputasi Paralel
