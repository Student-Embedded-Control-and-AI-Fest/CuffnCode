# Evaluasi 3 - Komputasi Paralel (IFB 206)

**Nama:** [Isi Nama Kamu]  
**NRP:** [Isi NRP Kamu]  
**Kelas:** Individu  

## Deskripsi Proyek
Proyek ini mengimplementasikan algoritma Perkalian Matriks (*Matrix Multiplication*) berukuran 500x500 menggunakan dua pendekatan untuk dianalisis performanya:
1. **Pendekatan Sekuensial:** Menggunakan perulangan bersarang konvensional (Single-Thread).
2. **Pendekatan Paralel:** Menggunakan pustaka **OpenMP** dengan direktif `#pragma omp parallel for collapse(2)` untuk mendistribusikan beban kalkulasi ke seluruh core prosesor yang tersedia (Multi-Thread).

## Cara Menjalankan Program (GCC / G++)
Pastikan compiler Anda mendukung OpenMP, jalankan perintah berikut di terminal:
```bash
g++ -fopenmp main.cpp -o program_paralel
./program_paralel