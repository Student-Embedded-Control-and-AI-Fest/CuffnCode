# Pemrosesan Banyak Gambar Lebih Cepat dengan Komputasi Paralel

---

## Anggota Kelompok

1. Raditya Rizky Wahyudi - 152024009
2. Bintang Albie Ilham Nidiputra - 152024034

---

## Deskripsi Singkat

Project ini adalah program Python sederhana yang digunakan untuk **membuktikan bahwa banyak gambar bisa diproses lebih cepat jika menggunakan komputasi paralel** dibandingkan diproses satu per satu (sequential).

Program akan membaca gambar dari folder `images/`, memproses setiap gambar (resize, grayscale, blur), lalu menyimpan hasilnya ke folder output. Di akhir program, akan ditampilkan **perbandingan waktu proses** antara metode sequential dan parallel di terminal.

---

## Tujuan Project

- Membuat program yang bisa memproses banyak gambar secara otomatis.
- Membandingkan dua metode pemrosesan: **sequential** dan **parallel**.
- Mengetahui perbedaan waktu proses dari kedua metode tersebut.
- Menunjukkan penerapan sederhana komputasi paralel **tanpa menggunakan hardware khusus**.

---

## Konsep Sequential Processing

**Sequential processing** adalah cara memproses data **satu per satu secara berurutan**.

Analoginya seperti antrian di kasir. Orang pertama harus selesai dilayani dulu, baru orang kedua bisa dilayani, lalu orang ketiga, dan seterusnya.

Dalam program ini, sequential berarti:
> Gambar pertama diproses sampai selesai → baru lanjut gambar kedua → baru lanjut gambar ketiga → dan seterusnya.

Jadi kalau ada 30 gambar, program harus menunggu gambar sebelumnya selesai dulu sebelum lanjut ke gambar berikutnya.

---

## Konsep Parallel Processing

**Parallel processing** adalah cara memproses data **secara bersamaan** menggunakan beberapa worker/proses.

Analoginya seperti kasir yang dibuka banyak. Kalau ada 4 kasir, maka 4 orang bisa dilayani secara bersamaan, sehingga antrian jadi lebih cepat selesai.

Dalam program ini, parallel berarti:
> Beberapa gambar diproses secara bersamaan oleh beberapa proses yang berjalan sekaligus.

Jadi kalau komputer punya 12 core CPU, program bisa memproses hingga 12 gambar secara bersamaan.

---

## Perbedaan Sequential dan Parallel

| Aspek | Sequential | Parallel |
|---|---|---|
| Cara kerja | Memproses gambar **satu per satu** | Memproses **beberapa gambar bersamaan** |
| Kecepatan | Lebih lambat untuk data banyak | **Lebih cepat** untuk data banyak |
| Kompleksitas | Lebih mudah dipahami | Membutuhkan pembagian proses |
| Penggunaan CPU | Hanya menggunakan 1 core | Menggunakan **banyak core** |
| Cocok untuk | Data sedikit | **Data dalam jumlah besar** |

**Ilustrasi:**

```
Sequential:
Gambar 1 ████████ selesai
                   Gambar 2 ████████ selesai
                                      Gambar 3 ████████ selesai
→ Total waktu = waktu gambar 1 + gambar 2 + gambar 3

Parallel:
Gambar 1 ████████ selesai
Gambar 2 ████████ selesai
Gambar 3 ████████ selesai
→ Total waktu = waktu 1 gambar saja (karena diproses bersamaan)
```

---

## Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| **Python** | Bahasa pemrograman utama yang digunakan untuk menulis program |
| **OpenCV** (`cv2`) | Library untuk memproses gambar (resize, grayscale, blur) |
| **multiprocessing** | Library bawaan Python untuk menjalankan proses secara paralel |
| **os** | Library bawaan Python untuk membaca folder dan file |
| **time** | Library bawaan Python untuk menghitung waktu proses |

---

## Struktur Folder

```
parallel-image-processing/
├── main.py                 # File utama program
├── requirements.txt        # Daftar library yang harus diinstall
├── README.md               # Dokumentasi project (file ini)
├── images/                 # Tempat menyimpan gambar input
├── output_sequential/      # Hasil gambar dari proses sequential
└── output_parallel/        # Hasil gambar dari proses parallel
```

**Penjelasan:**

| File / Folder | Fungsi |
|---|---|
| `main.py` | File utama yang berisi seluruh kode program |
| `requirements.txt` | Daftar library yang perlu diinstall sebelum menjalankan program |
| `README.md` | File dokumentasi yang menjelaskan isi project |
| `images/` | Folder tempat kita menaruh gambar-gambar yang akan diproses |
| `output_sequential/` | Folder untuk menyimpan hasil gambar yang diproses secara sequential |
| `output_parallel/` | Folder untuk menyimpan hasil gambar yang diproses secara parallel |

> **Catatan:** Folder `output_sequential/` dan `output_parallel/` akan dibuat otomatis oleh program jika belum ada.

---

## Alur Kerja Program

Berikut langkah-langkah yang dilakukan program saat dijalankan:

1. Program membaca semua gambar dari folder `images/`.
2. Program memproses semua gambar secara **sequential** (satu per satu).
3. Program mencatat berapa lama waktu proses sequential.
4. Program memproses semua gambar secara **parallel** (bersamaan).
5. Program mencatat berapa lama waktu proses parallel.
6. Hasil gambar yang sudah diproses disimpan ke folder `output_sequential/` dan `output_parallel/`.
7. Program menampilkan **perbandingan waktu** di terminal.

```
Program Dimulai
      │
      ▼
Baca semua gambar dari folder images/
      │
      ├── Tidak ada gambar? → Tampilkan pesan error → Selesai
      │
      ▼
Proses SEQUENTIAL (satu per satu)
  → Resize → Grayscale → Blur → Simpan ke output_sequential/
  → Catat waktu proses
      │
      ▼
Proses PARALLEL (bersamaan)
  → Resize → Grayscale → Blur → Simpan ke output_parallel/
  → Catat waktu proses
      │
      ▼
Tampilkan perbandingan waktu di terminal
      │
      ▼
Program Selesai
```

---

## Proses Pengolahan Gambar

Setiap gambar yang dibaca akan melewati 3 tahapan pengolahan:

| Tahap | Proses | Penjelasan |
|---|---|---|
| 1 | **Resize** | Menyamakan ukuran semua gambar menjadi ukuran yang sama (500x500 piksel) |
| 2 | **Grayscale** | Mengubah gambar berwarna menjadi hitam putih |
| 3 | **Blur** | Memberi efek halus pada gambar (menghaluskan detail) |

Ketiga tahapan ini diterapkan pada setiap gambar, baik saat proses sequential maupun parallel. Hasilnya kemudian disimpan ke folder output masing-masing.

---

## Cara Install dan Menjalankan Program

### 1. Install Library

Buka terminal atau command prompt, masuk ke folder project, lalu jalankan:

```bash
pip install -r requirements.txt
```

Perintah ini akan menginstall library **OpenCV** yang dibutuhkan program.

### 2. Siapkan Gambar

Masukkan beberapa gambar ke folder `images/`. Format yang didukung:
- `.jpg`
- `.jpeg`
- `.png`

> **Tips:** Semakin banyak gambar yang dimasukkan, semakin terlihat perbedaan waktu antara sequential dan parallel.

### 3. Jalankan Program

```bash
python main.py
```

Program akan otomatis memproses gambar dan menampilkan hasil perbandingan waktu di terminal.

---

## Contoh Output Terminal

```
=======================================================
 PEMROSESAN BANYAK GAMBAR DENGAN KOMPUTASI PARALEL
=======================================================

Ditemukan 30 gambar di folder 'images'.

[1] Memulai pemrosesan SEQUENTIAL...
    Memproses 30 gambar satu per satu.

    [1/30] Selesai: images\gambar01.jpg
    [2/30] Selesai: images\gambar02.jpg
    ...
    [30/30] Selesai: images\gambar30.jpg

    Pemrosesan sequential selesai dalam 8.7395 detik.

[2] Memulai pemrosesan PARALLEL...
    Memproses 30 gambar dengan 12 proses.

    Pemrosesan parallel selesai dalam 2.5269 detik.

=======================================================
        HASIL PERBANDINGAN WAKTU PROSES
=======================================================
  Jumlah gambar diproses  : 30 gambar
  Waktu sequential        : 8.7395 detik
  Waktu parallel          : 2.5269 detik
  Selisih waktu           : 6.2125 detik
  Speedup                 : 3.46x
  Metode lebih cepat      : Parallel
=======================================================

  Kesimpulan: Metode Parallel lebih cepat
  dengan selisih 6.2125 detik.
```

---

## Penjelasan Hasil

Dari contoh output di atas, bisa dilihat bahwa:

- Metode **sequential** membutuhkan waktu **8.74 detik** untuk memproses 30 gambar.
- Metode **parallel** hanya membutuhkan waktu **2.53 detik** untuk memproses gambar yang sama.
- Metode parallel **3.46x lebih cepat** dibandingkan sequential.

Kenapa bisa lebih cepat? Karena pada metode parallel, program **tidak memproses gambar satu per satu**. Program membagi pekerjaan ke beberapa proses yang berjalan bersamaan, sehingga beberapa gambar bisa diproses sekaligus.

> **Catatan:** Semakin banyak jumlah gambar, semakin terlihat perbedaan kecepatannya. Untuk jumlah gambar yang sangat sedikit (misalnya 2-3 gambar), perbedaannya mungkin tidak terlalu signifikan karena ada overhead saat membuat proses paralel.

---

## Kesimpulan

Project ini menunjukkan bahwa **komputasi paralel dapat membantu mempercepat proses pengolahan banyak gambar**. Dengan membandingkan waktu sequential dan parallel, kita bisa melihat bahwa:

- **Sequential**: cocok untuk data sedikit, prosesnya sederhana tapi lebih lambat.
- **Parallel**: cocok untuk data banyak, prosesnya lebih cepat karena pekerjaan dibagi ke beberapa proses.

Parallel processing sangat bermanfaat dalam dunia nyata, terutama untuk pekerjaan yang melibatkan **data dalam jumlah besar** seperti pengolahan gambar, video, atau data ilmiah.

---