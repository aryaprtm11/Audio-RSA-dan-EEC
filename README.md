# Steganografi Audio dengan ECC, RSA, dan DWT

Proyek ini merupakan implementasi steganografi teks ke audio menggunakan kombinasi enkripsi ECC dan RSA dengan teknik penyembunyian data DWT (Discrete Wavelet Transform) pada file audio.

## Fitur

- Enkripsi ganda pesan menggunakan algoritma ECC dan RSA
- Penyembunyian data dalam file audio dengan teknik DWT (Discrete Wavelet Transform)
- Ekstraksi dan dekripsi pesan dari file audio yang telah disisipi
- Mode interaktif melalui GUI atau terminal

## Instalasi

1. Pastikan Python (versi 3.8 atau yang lebih baru) sudah terinstal
2. Install dependensi yang diperlukan:

```bash
pip install -r requirements.txt
```

## Penggunaan

### Menjalankan Program Steganografi (ECC+RSA+DWT)

Jalankan salah satu mode berikut:

**GUI:**

```bash
python src/GUI.py
```

**Terminal (CLI):**

```bash
python src/cli.py
```

Ikuti instruksi pada layar untuk melakukan enkripsi, penyisipan, ekstraksi, dan dekripsi pesan.

## Struktur Kode

- `src/core.py` : Integrasi utama ECC, RSA, dan DWT, serta workflow steganografi.
- `src/crypto/` : Implementasi algoritma ECC (`ecc.py`) dan RSA (`rsa.py`).
- `src/steg/dwt.py` : Implementasi penyisipan dan ekstraksi data menggunakan DWT.
- `src/evaluations/` : Modul evaluasi (time performance, entropy, SNR, listening test).
- `src/utils/` : Utilitas pendukung.

## Evaluasi Sistem

### 1. Time Performance

- Mengukur waktu proses enkripsi, penyisipan, ekstraksi, dan dekripsi.
- Setiap proses diulang 5x, hasil divisualisasikan dalam bar chart.
- Overhead adalah tambahan waktu akibat proses enkripsi dan penyisipan.
- Output: file chart di `src/evaluations/output/time_performance/`.

Jalankan:

```bash
python src/evaluations/time_performance.py
```

### 2. Entropy

- Mengukur tingkat keacakan (randomness) audio sebelum dan sesudah penyisipan.
- Entropi tinggi menandakan audio sulit dibedakan secara statistik.
- Output: chart dan nilai entropi di `src/evaluations/output/entropy/`.

Jalankan:

```bash
python src/evaluations/entropy.py
```

### 3. SNR (Signal-to-Noise Ratio)

- Membandingkan kualitas audio asli dan stego (setelah penyisipan).
- SNR tinggi menandakan kualitas audio stego mendekati aslinya.
- Output: nilai SNR di `src/evaluations/output/snr/`.

Jalankan:

```bash
python src/evaluations/snr.py
```

### 4. Listening Test

- Evaluasi subjektif kualitas audio stego oleh pendengar.
- Hasil divisualisasikan dalam chart deskriptif (bukan persentase 100%).
- Output: chart di `src/evaluations/output/listening_test/`.

Jalankan:

```bash
python src/evaluations/listening_test.py
```

## Penjelasan Hasil Evaluasi

- **Time Performance:** Semakin kecil waktu, semakin efisien sistem. Overhead menunjukkan tambahan waktu akibat proses keamanan.
- **Entropy:** Nilai entropi yang tidak berubah signifikan menandakan penyisipan tidak merusak keacakan audio.
- **SNR:** Nilai SNR tinggi berarti kualitas audio stego tetap baik.
- **Listening Test:** Hasil deskriptif menunjukkan persepsi pendengar terhadap kualitas audio stego.

## Referensi & Kontak

- Lihat folder `docs/` untuk teori dan penjelasan lebih lanjut.
- Untuk pertanyaan, hubungi pengembang melalui email atau kontak yang tertera di laporan.
