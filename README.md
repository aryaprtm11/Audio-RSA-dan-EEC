# Steganografi Audio dengan ECC, RSA, dan DWT

Proyek ini merupakan implementasi steganografi teks ke audio menggunakan kombinasi enkripsi ECC dan RSA dengan teknik penyembunyian data DWT (Discrete Wavelet Transform) pada file audio.

## Fitur

- Enkripsi ganda pesan menggunakan algoritma ECC dan RSA
- Penyembunyian data dalam file audio dengan teknik DWT (Discrete Wavelet Transform)
- Ekstraksi dan dekripsi pesan dari file audio yang telah disisipi
- Mode interaktif melalui gui atau terminal

## Instalasi

1. Pastikan Python (versi 3.8 atau yang lebih baru) sudah terinstal
2. Install dependensi yang diperlukan:

```
pip install -r requirements.txt
```

## Penggunaan

### Program Steganografi dengan Enkripsi Ganda (ECC+RSA)

```
python src/gui.py
```

atau

```
python src/cli.py
```
