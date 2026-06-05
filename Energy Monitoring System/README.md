⚡ Energy Monitoring System

Energy Monitoring System adalah sebuah aplikasi web sederhana yang dirancang untuk memantau dan mengelola konsumsi daya listrik pada berbagai perangkat di dalam beberapa ruangan. Aplikasi ini dilengkapi dengan dashboard *real-time*, grafik penggunaan daya, serta fitur proteksi kelebihan beban (Overload Protection).

#  Fitur Utama

- **Kelola Room (Ruangan):** Menambahkan ruangan baru atau menghapus ruangan beserta seluruh perangkat di dalamnya.
- **Kelola Device (Perangkat):** Fitur CRUD (Create, Read, Update, Delete) lengkap untuk mendaftarkan perangkat listrik, mengubah detail perangkat, dan menghapusnya.
- **Toggle ON/OFF Real-time:** Menyalakan atau mematikan perangkat dengan pembaruan data secara langsung (*real-time*).
- **Overload Protection:** Validasi otomatis yang mencegah pengguna menyalakan perangkat jika total beban di satu ruangan akan melebihi **1000 Watt**.
- **Live Dashboard:** Menampilkan statistik metrik penting seperti Total Building Watt, Total Rooms, Active Devices, dan Efficiency Score.
- **Power Usage History:** Grafik garis interaktif (menggunakan Chart.js) yang memvisualisasikan riwayat beban listrik selama 60 detik terakhir.
- **Sistem Rekomendasi:** Memberikan peringatan status penggunaan energi (Normal, High, atau Critical) berdasarkan total pemakaian daya.

# Teknologi yang Digunakan

**Backend:**
- Python 3
- Flask (Micro-framework)

**Frontend:**
- HTML5 & CSS3
- Google Fonts (Poppins)
- Vanilla JavaScript (Fetch API untuk interaksi asinkron)
- [Chart.js](https://www.chartjs.org/) (Untuk visualisasi data grafik)

# Struktur Direktori

Pastikan struktur file dan folder Anda terlihat seperti ini sebelum menjalankan aplikasi:

energy monitoring system/
│
├── app.py             
├── templates/
│   └── index.html   
└── static/
    ├── style.css         
    └── script.js         