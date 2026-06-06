# Evaluasi-3-Komputasi-Paralel-Najwan-152024079
# Dokumentasi Evaluasi 3 - Komputasi Paralel (IFB 206)

## Data Mahasiswa
* **Nama:** Muhammad Najwan A
* **NRP:** 152024079
* **Mata Kuliah:** IFB 206 Komputasi Paralel
* **Dosen Pengampu:** Lisa Kristiana Ph.D

---

## 1. Deskripsi Proyek (CuffnCode)
Implementasi kontrol tertanam dan kecerdasan buatan (*Embedded Control and AI*) menggunakan teknik komputasi paralel (*multiprocessing*) di Python untuk mengoptimalkan performa pemrosesan data secara simultan.

---

## 2. Kode Utama Pemrosesan Paralel
```python
import multiprocessing
import time

def proses_paralel(data):
    return data * data

if __name__ == "__main__":
    kumpulan_data = [1, 2, 3, 4, 5]
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        hasil = pool.map(proses_paralel, kumpulan_data)
    print("Hasil eksekusi paralel:", hasil)
