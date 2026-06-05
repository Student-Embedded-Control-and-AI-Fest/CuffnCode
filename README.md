# Parallel File Analyzer

## Evaluasi 3

### Mata Kuliah
Komputasi Paralel dan Sistem Terdistribusi

---

## Latar Belakang

Komputasi paralel merupakan teknik menjalankan beberapa proses secara bersamaan untuk meningkatkan efisiensi komputasi.

Python menyediakan modul multiprocessing yang memungkinkan pemanfaatan beberapa CPU core secara bersamaan.

---

## Tujuan

- Memahami konsep komputasi paralel.
- Mengimplementasikan multiprocessing.
- Melakukan analisis beberapa file secara bersamaan.

---

## Metode

Program membaca lima file text.

Setiap file diproses oleh process yang berbeda menggunakan multiprocessing Pool.

Informasi yang dihitung:

- Jumlah baris
- Jumlah kata
- Jumlah karakter
- Kata yang paling sering muncul

---

## Flowchart

```
Start

↓

Load Files

↓

Create Process Pool

↓

Analyze File 1

Analyze File 2

Analyze File 3

Analyze File 4

Analyze File 5

↓

Collect Result

↓

Display Output

↓

Finish
```

---

## Hasil

Program berhasil memproses lima file secara paralel.

Contoh output:

| File | Words | Lines |
|------|---------|---------|
|file1.txt|19|4|
|file2.txt|17|3|
|file3.txt|12|2|
|file4.txt|15|3|
|file5.txt|15|3|

---

## Developer

Nama : Rizky Rifansa Alfariz
NIM : 152024176
Kelas : CC