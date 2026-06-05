# Dokumentasi Logika Firmware CuffnCode

File `Firmware.ino` berisi kerangka logika (skeleton code) untuk mengontrol perangkat keras alat pengukur tekanan darah (sphygmomanometer) secara digital menggunakan mikrokontroler **STM32F411CE (Black Pill)**.

## Komponen Utama dalam Kode

### 1. Definisi Pin (Perangkat Keras)
Kode ini mengatur jalur (pin) komunikasi antara otak mikrokontroler dengan perangkat lunak maupun mekanik:
* **`SENSOR_PIN` (PA0)**: Berfungsi membaca sinyal analog dari sensor tekanan darah (MPS20N0040D) yang sudah diperkuat oleh modul *Analog Front End* (AFE).
* **`PUMP_PIN` (PB0)**: Berfungsi menyalakan atau mematikan pompa udara untuk mengontrol pemompaan manset lengan.
* **`VALVE_PIN` (PB1)**: Berfungsi membuka atau menutup katup untuk menahan atau membuang udara.

### 2. Alur Pengukuran Tekanan Darah (State Machine)
Sistem pengukur tekanan darah bekerja secara berurutan. Secara konsep (yang tergambar pada fungsi `loop`), prosesnya dibagi menjadi beberapa tahapan logis:
1. **IDLE (Menunggu)**: Sistem diam dan aman (katup terbuka, pompa mati), menunggu instruksi untuk memulai pengukuran.
2. **INFLATE (Memompa)**: Katup pembuangan ditutup, lalu pompa udara dinyalakan hingga tekanan di dalam manset mencapai batas target (*Target Pressure*, contoh: 160 mmHg).
3. **DEFLATE & MEASURE (Pembuangan & Pengukuran)**: Pompa dimatikan, dan katup udara mulai dibuka sedikit demi sedikit agar udara keluar secara perlahan. Di fase inilah sensor terus-menerus membaca tekanan dan mencari sinyal detak nadi (osilasi).
4. **CALCULATE (Perhitungan)**: Dari kumpulan data osilasi tekanan yang diukur pada tahap sebelumnya, mikrokontroler akan mengekstraksi dan menghitung nilai batas atas (Sistolik) dan batas bawah (Diastolik).
5. **FINISH (Selesai)**: Proses selesai. Katup udara dibuka sepenuhnya untuk mengempiskan manset dengan sangat cepat demi kenyamanan pengguna.

### 3. Filter Digital (Peredam Noise)
Sinyal osilasi detak nadi manusia sangatlah kecil jika dibandingkan dengan tekanan udara total. Sinyal kecil ini sangat rentan terkena gangguan/interferensi dari listrik di sekitar kita (humming 50Hz/60Hz dari jaringan PLN).
Untuk mengatasi ini, disiapkan algoritma perhitungan matematika bernama **Notch Filter 50Hz** pada fungsi `applyNotchFilter()`. Algoritma ini bertugas meredam atau menghilangkan frekuensi pengganggu secara digital sehingga sinyal aslinya menjadi lebih bersih dan mudah dibaca.

### 4. Konversi Nilai Tekanan (Fungsi `readPressure`)
Sinyal awal yang terbaca oleh mikrokontroler masih berupa nilai *raw ADC* (0 hingga 4095). Fungsi ini bertugas mengubah angka tersebut menjadi tegangan volt (0v - 3.3v).
> **Catatan Kalibrasi Penting:** Di dalam fungsi ini, Anda nantinya wajib menambahkan rumus linier / *calibration curve* milik Anda sendiri. Tujuannya adalah untuk mengonversi nilai voltase tersebut menjadi satuan metrik baku pengukur tekanan darah, yaitu **mmHg**.

## Langkah Pengembangan Selanjutnya
- **Pengecekan Pin:** Pastikan `PA0`, `PB0`, dan `PB1` sudah cocok dan sesuai dengan jalur skematik PCB/KiCad nyata yang sedang Anda kerjakan.
- **Penyesuaian Filter Digital:** Angka-angka di dalam Notch Filter saat ini dikalkulasikan berdasarkan asumsi *sample rate* atau seberapa cepat mikrokontroler mengambil data dari sensor (saat ini diset ilustratif 500 Hz). Jika frekuensi pengambilan sampel berubah, angka perhitungannya (`b0, b1, a1, dll`) juga perlu dirancang ulang.
- **Menulis Rumus Osilometrik:** Anda harus melengkapi kode di fungsi `loop()` yang secara spesifik akan menghitung bagaimana tekanan Sistolik (SYS) dan Diastolik (DIA) diekstrak.
