# Steganografi Audio dengan ECC, RSA, dan DWT

Proyek ini merupakan implementasi steganografi teks ke audio menggunakan kombinasi enkripsi ECC dan RSA dengan teknik penyembunyian data DWT (Discrete Wavelet Transform) pada file audio.

## Fitur

- Enkripsi ganda pesan menggunakan algoritma ECC dan RSA
- Penyembunyian data dalam file audio dengan teknik DWT (Discrete Wavelet Transform)
- Ekstraksi dan dekripsi pesan dari file audio yang telah disisipi
- Mode interaktif melalui terminal

## Instalasi

1. Pastikan Python (versi 3.8 atau yang lebih baru) sudah terinstal
2. Install dependensi yang diperlukan:

```
pip install -r requirements.txt
```

## Penggunaan

### Program Steganografi dengan Enkripsi Ganda (ECC+RSA)

```
python src/interactive_steg_combined.py
```

Program ini menyediakan opsi:
1. Sisipkan pesan dalam file audio (dengan enkripsi ganda ECC+RSA)
2. Ekstrak pesan dari file audio 
3. Debug ekstraksi (untuk membantu mendiagnosis masalah)
4. Keluar

### Program Steganografi dengan ECC saja

```
python src/interactive_steg_ecc_fixed.py
```

Program ini menyediakan opsi:
1. Sisipkan pesan dalam file audio (dengan enkripsi ECC)
2. Ekstrak pesan dari file audio
3. Keluar

## Komponen Utama

- `ecc_simple.py`: Implementasi algoritma ECC untuk enkripsi dan dekripsi
- `rsa_simple.py`: Implementasi algoritma RSA untuk enkripsi dan dekripsi
- `dwt.py`: Implementasi teknik Discrete Wavelet Transform untuk penyembunyian data
- `interactive_steg_combined.py`: Program utama dengan kombinasi ECC dan RSA
- `interactive_steg_ecc_fixed.py`: Program alternatif dengan ECC saja

## Catatan Penting

- Nilai parameter `alpha` dalam DWT memengaruhi kualitas hasil steganografi. Nilai default adalah 0.1.
- Kunci publik dan privat disimpan dalam file `.key` dan informasi embedding disimpan dalam file `.info`
- Dalam aplikasi nyata, kunci privat harus disimpan dengan aman dan tidak disertakan dalam file stego

## Kontributor

- [Nama Anda] 