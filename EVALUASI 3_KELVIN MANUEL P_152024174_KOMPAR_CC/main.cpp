#include <iostream>
#include <vector>
#include <omp.h>

/**
 * @brief Fungsi untuk melakukan perkalian matriks secara sekuensial (tunggal)
 */
void perkalianMatriksSekuensial(int N, const std::vector<std::vector<double>>& A, 
                                const std::vector<std::vector<double>>& B, 
                                std::vector<std::vector<double>>& C) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

/**
 * @brief Fungsi untuk melakukan perkalian matriks secara paralel menggunakan OpenMP
 */
void perkalianMatriksParalel(int N, const std::vector<std::vector<double>>& A, 
                             const std::vector<std::vector<double>>& B, 
                             std::vector<std::vector<double>>& C) {
    // Direktif OpenMP untuk membagi beban kerja loop ke beberapa Core/Thread CPU
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    std::cout << "========================================================\n";
    std::cout << "  EVALUASI 3 - IFB 206 KOMPUTASI PARALEL (INDIVIDU)     \n";
    std::cout << "========================================================\n\n";

    // Ukuran matriks N x N (500x500 cukup berat untuk simulasi perbedaan waktu)
    int N = 500; 
    
    // Inisialisasi matriks dengan data dummy
    std::vector<std::vector<double>> A(N, std::vector<double>(N, 1.5));
    std::vector<std::vector<double>> B(N, std::vector<double>(N, 2.5));
    std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

    // -----------------------------------------------------------------
    // 1. PENGUJIAN SEKUENSIAL (LOGIKA BIASA / 1 THREAD)
    // -----------------------------------------------------------------
    std::cout << "[*] Menjalankan Pengujian Sekuensial..." << std::endl;
    double start_sekuensial = omp_get_wtime();
    perkalianMatriksSekuensial(N, A, B, C);
    double end_sekuensial = omp_get_wtime();
    double waktu_sekuensial = end_sekuensial - start_sekuensial;
    std::cout << "[+] Selesai. Waktu Eksekusi Sekuensial: " << waktu_sekuensial << " detik.\n\n";

    // Reset matriks hasil sebelum pengujian paralel
    std::fill(C.begin(), C.end(), std::vector<double>(N, 0.0));

    // -----------------------------------------------------------------
    // 2. PENGUJIAN PARALEL (MENGGUNAKAN MULTI-THREADING OPENMP)
    // -----------------------------------------------------------------
    std::cout << "[*] Menjalankan Pengujian Paralel (OpenMP)..." << std::endl;
    double start_paralel = omp_get_wtime();
    perkalianMatriksParalel(N, A, B, C);
    double end_paralel = omp_get_wtime();
    double waktu_paralel = end_paralel - start_paralel;
    std::cout << "[+] Selesai. Waktu Eksekusi Paralel   : " << waktu_paralel << " detik.\n\n";

    // -----------------------------------------------------------------
    // 3. ANALISIS PERFORMA & KESIMPULAN
    // -----------------------------------------------------------------
    double speedup = waktu_sekuensial / waktu_paralel;
    
    std::cout << "==================== KESIMPULAN ========================\n";
    std::cout << "Ukuran Matriks     : " << N << " x " << N << "\n";
    std::cout << "Waktu Sekuensial   : " << waktu_sekuensial << " detik\n";
    std::cout << "Waktu Paralel      : " << waktu_paralel << " detik\n";
    std::cout << "Peningkatan Performa: Komputasi Paralel " << speedup << "x lebih cepat!\n";
    std::cout << "========================================================\n";

    return 0;
}