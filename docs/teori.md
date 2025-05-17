# Konsep Teoritis Steganografi Audio dengan DWT dan RSA

## Steganografi Audio

Steganografi audio adalah teknik untuk menyembunyikan informasi rahasia dalam file audio dengan cara yang tidak terdeteksi oleh indra pendengaran manusia. Berbeda dengan enkripsi yang membuat pesan tidak dapat dibaca tetapi keberadaannya dapat diketahui, steganografi berfokus pada menyembunyikan keberadaan pesan itu sendiri.

## Discrete Wavelet Transform (DWT)

### Konsep Dasar DWT

DWT adalah metode untuk menganalisis sinyal ke dalam komponen frekuensi yang berbeda-beda dalam domain waktu. Berbeda dengan transformasi Fourier yang hanya memberikan informasi frekuensi, DWT menyediakan informasi frekuensi dan waktu secara bersamaan.

### Proses DWT dalam Steganografi Audio

1. **Dekomposisi Sinyal**: Sinyal audio dipecah menjadi koefisien detail (high-frequency) dan koefisien aproksimasi (low-frequency) pada level yang berbeda.

2. **Pemilihan Subband untuk Penyisipan**: Perubahan pada koefisien detail biasanya kurang terdeteksi secara auditory, sehingga pesan rahasia disisipkan pada koefisien detail.

3. **Penyisipan Pesan**: Bit pesan disisipkan dengan memodifikasi nilai koefisien detail. Nilai koefisien diubah berdasarkan bit yang akan disisipkan.

4. **Rekonstruksi Sinyal**: Setelah penyisipan, koefisien DWT diubah kembali menjadi sinyal audio menggunakan Inverse DWT (IDWT).

### Kelebihan DWT untuk Steganografi Audio

- **Robustness**: Lebih tahan terhadap manipulasi sinyal seperti kompresi atau filtering
- **Imperceptibility**: Perubahan pada domain wavelet sulit dideteksi oleh pendengaran manusia
- **Kapasitas**: Dapat menyisipkan informasi dalam jumlah yang cukup besar
- **Security**: Memberikan lapisan keamanan tambahan karena kompleksitas transformasi

## Algoritma RSA

### Konsep Dasar RSA

RSA adalah algoritma kriptografi asimetris yang menggunakan sepasang kunci: kunci publik untuk enkripsi dan kunci privat untuk dekripsi. Keamanan RSA terletak pada kesulitan memfaktorkan hasil kali dari dua bilangan prima yang besar.

### Langkah-langkah Algoritma RSA

1. **Pemilihan Dua Bilangan Prima**: Pilih dua bilangan prima p dan q
2. **Perhitungan Modulus**: Hitung n = p × q
3. **Perhitungan Fungsi Totient Euler**: φ(n) = (p - 1) × (q - 1)
4. **Pemilihan Kunci Publik (e)**: Pilih e dimana 1 < e < φ(n) dan e relatif prima dengan φ(n)
5. **Perhitungan Kunci Privat (d)**: Hitung d dimana (d × e) mod φ(n) = 1
6. **Enkripsi**: Untuk pesan m, ciphertext c = m^e mod n
7. **Dekripsi**: Untuk ciphertext c, pesan m = c^d mod n

## Fungsi Hash SHA-256

### Konsep Dasar SHA-256

SHA-256 (Secure Hash Algorithm 256-bit) adalah fungsi hash kriptografis yang menghasilkan nilai hash 256-bit (32 byte) dari data input. Fungsi hash ini memiliki sifat:

- **One-way function**: Tidak mungkin mendapatkan data input dari nilai hash
- **Deterministic**: Input yang sama selalu menghasilkan hash yang sama
- **Collision-resistant**: Sangat sulit menemukan dua input berbeda yang menghasilkan hash yang sama

### Peran SHA-256 dalam Steganografi

Dalam implementasi ini, SHA-256 digunakan untuk:
1. **Verifikasi Integritas**: Memastikan pesan yang diekstrak tidak mengalami perubahan
2. **Autentikasi**: Memverifikasi bahwa pesan berasal dari pengirim yang dimaksud

## Integrasi DWT, RSA, dan SHA-256 dalam Steganografi Audio

### Proses Penyembunyian (Embedding)

1. **Enkripsi dengan RSA**: Pesan teks dienkripsi menggunakan kunci publik RSA
2. **Hashing dengan SHA-256**: Hash dari pesan asli dihitung
3. **Persiapan Header**: Header berisi informasi tentang hash dan kunci publik
4. **Konversi ke Bit**: Header dan pesan terenkripsi dikonversi ke representasi bit
5. **Penerapan DWT**: Sinyal audio ditransformasi menggunakan DWT
6. **Penyisipan Bit**: Bit dari header dan pesan terenkripsi disisipkan pada koefisien detail DWT
7. **Rekonstruksi Audio**: Audio direkonstruksi menggunakan IDWT

### Proses Ekstraksi

1. **Penerapan DWT**: Sinyal audio yang berisi pesan disembunyikan ditransformasi menggunakan DWT
2. **Ekstraksi Bit**: Bit dari header dan pesan diekstrak dari koefisien detail DWT
3. **Parsing Header**: Header diurai untuk mendapatkan hash dan informasi kunci publik
4. **Dekripsi dengan RSA**: Pesan terenkripsi didekripsi menggunakan kunci privat RSA
5. **Verifikasi dengan SHA-256**: Hash dari pesan yang diekstrak dihitung dan dibandingkan dengan hash di header

## Keamanan Sistem

Keamanan sistem steganografi audio dengan DWT dan RSA ini didasarkan pada:

1. **Multiple Security Layers**: Kombinasi steganografi (DWT) dan kriptografi (RSA)
2. **Kriptografi Asimetris**: Pesan dienkripsi dengan RSA yang aman secara matematis
3. **Domain Transformasi**: Penyisipan dilakukan pada domain transformasi, bukan domain waktu langsung
4. **Verifikasi Integritas**: Penggunaan SHA-256 untuk memastikan integritas pesan

## Batasan dan Pertimbangan

1. **Kapasitas**: Jumlah bit yang dapat disisipkan terbatas oleh ukuran file audio
2. **Kualitas Audio**: Penyisipan terlalu banyak data dapat memengaruhi kualitas audio
3. **Ketahanan (Robustness)**: Ketahanan terhadap kompresi atau manipulasi audio bisa terbatas
4. **Kompleksitas Komputasi**: Proses DWT dan operasi RSA membutuhkan daya komputasi yang cukup besar 