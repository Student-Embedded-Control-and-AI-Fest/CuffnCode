import streamlit as st
import os
import time
from concurrent.futures import ProcessPoolExecutor
import worker  # Mengimpor modul worker terpisah

st.set_page_config(page_title="Parallel Image Processor", layout="wide")

st.title("🚀 Website Pemrosesan Gambar Massal - Komputasi Paralel")
st.subheader("Evaluasi 3 - Proyek Optimasi Independen")

# Setup Direktori
INPUT_DIR = "input_images"
OUTPUT_DIR = "output_images"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sidebar untuk upload gambar sampel
st.sidebar.header("📁 Unggah Gambar Sampel")
uploaded_files = st.sidebar.file_uploader("Pilih beberapa gambar (JPG/PNG)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if uploaded_files:
    # Simpan file yang diunggah ke folder input
    for f in uploaded_files:
        with open(os.path.join(INPUT_DIR, f.name), "wb") as buffer:
            buffer.write(f.getbuffer())
    st.sidebar.success(f"{len(uploaded_files)} Gambar berhasil disiapkan di lokal!")

# Ambil daftar gambar yang siap diproses
image_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(('jpg', 'jpeg', 'png'))]

st.write(f"**Total Gambar Siap Proses:** {len(image_files)} file.")

if st.button("🔥 Jalankan Komparasi Performa (Sekuensial vs Paralel)", type="primary"):
    if len(image_files) == 0:
        st.error("Silakan unggah gambar terlebih dahulu melalui sidebar!")
    else:
        # Menyiapkan argumen tuple untuk fungsi multiprocessing
        task_args = [(img_path, OUTPUT_DIR) for img_path in image_files]
        
        # 1. EKSEKUSI SEKUENSIAL
        st.info("Menjalankan Mode Sekuensial (Single-Thread)...")
        start_seq = time.time()
        for arg in task_args:
            worker.process_single_image(arg)
        t_sekuensial = time.time() - start_seq
        st.success(f"⏱️ Sekuensial Selesai: {t_sekuensial:.2f} detik")

        # 2. EKSEKUSI PARALEL
        st.info("Menjalankan Mode Paralel (Multi-Processing)...")
        start_par = time.time()
        # ProcessPoolExecutor otomatis mendeteksi jumlah Core CPU laptopmu
        with ProcessPoolExecutor() as executor:
            list(executor.map(worker.process_single_image, task_args))
        t_paralel = time.time() - start_par
        st.success(f"⚡ Paralel Selesai: {t_paralel:.2f} detik")

        # 3. ANALISIS SPEEDUP & METRIK
        speedup = t_sekuensial / t_paralel
        
        st.markdown("---")
        st.header("📊 Hasil Analisis Performa")
        
        col1, col2 = st.columns(2)
        with col1:
            # Tampilkan data komparasi dalam bentuk grafik batang
            chart_data = {
                "Metode Execution": ["Sekuensial", "Paralel"],
                "Waktu (Detik)": [t_sekuensial, t_paralel]
            }
            st.bar_chart(data=chart_data, x="Metode Execution", y="Waktu (Detik)")
            
        with col2:
            st.metric(label="Peningkatan Kecepatan (Speedup)", value=f"{speedup:.2f}x Lebih Cepat")
            st.markdown(f"> Dengan arsitektur paralel, sistem berhasil membagi beban kerja pemrosesan filter gambar ke seluruh core prosesor secara merata.")