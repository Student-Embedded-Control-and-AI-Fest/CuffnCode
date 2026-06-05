# Parallel File Analyzer

## Evaluasi 3

### Mata Kuliah
Komputasi Paralel dan Sistem Terdistribusi

### Nama
Rizky Rifansa Alfariz

### NIM
152024176

---

# Deskripsi Project

Parallel File Analyzer merupakan aplikasi sederhana yang dibuat menggunakan bahasa Python dengan memanfaatkan konsep komputasi paralel (Multiprocessing).

Program ini melakukan analisis terhadap beberapa file teks secara bersamaan.

---

# Tujuan

- Memahami konsep komputasi paralel.
- Mengimplementasikan multiprocessing pada Python.
- Menganalisis beberapa file secara bersamaan.

---

# Cara Kerja Program

1. Program membaca seluruh file text pada folder data.
2. Program membuat beberapa process menggunakan Multiprocessing Pool.
3. Setiap process menganalisis satu file.
4. Hasil seluruh process digabungkan.
5. Program menampilkan hasil analisis.

---

# Informasi yang Dianalisis

Setiap file akan dihitung:

- Jumlah Baris
- Jumlah Kata
- Jumlah Karakter
- Kata yang Paling Sering Muncul

---

# Flowchart

```
Start

↓

Load File

↓

Create Multiprocessing Pool

↓

Analyze File 1
Analyze File 2
Analyze File 3
Analyze File 4
Analyze File 5

↓

Collect Result

↓

Display Result

↓

Finish
```

---

# Hasil Pengujian

Contoh output program:

```
PARALLEL FILE ANALYZER

File : data/file1.txt
Lines : 4
Words : 19
Characters : 140
Most Frequent : python

Execution Time : 0.308 second
```

---

# Teknologi yang Digunakan

- Python 3
- Multiprocessing
- Collections Counter
- GitHub

---

# Kesimpulan

Program berhasil mengimplementasikan konsep komputasi paralel menggunakan multiprocessing Python untuk melakukan analisis beberapa file secara bersamaan.

Teknik ini dapat meningkatkan efisiensi pemrosesan data dibandingkan proses serial.

---

## Institut Teknologi Nasional Bandung

Semester Genap 2025/2026