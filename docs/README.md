# Dokumentasi Steganografi Audio

Folder ini berisi dokumentasi dari implementasi Steganografi Audio menggunakan RSA, SHA-256, dan DWT.

## Daftar Isi

1. [Konsep Teoritis](teori.md) - Penjelasan tentang konsep teoritis steganografi audio, DWT, RSA, dan SHA-256

## Penjelasan Cara Kerja

Implementasi ini menggunakan pendekatan tiga lapis keamanan:

1. **Enkripsi dengan RSA**: Pesan awal dienkripsi dengan algoritma RSA untuk melindungi isi pesan
2. **Hashing dengan SHA-256**: Pesan asli dihashing dengan SHA-256 untuk memverifikasi integritas saat ekstraksi
3. **Penyembunyian dengan DWT**: Pesan terenkripsi dan hash disisipkan ke dalam koefisien detail DWT dari file audio

## Alur Program

### Proses Penyembunyian (Embed)

1. Pengguna memberikan file audio asli, file audio output, dan pesan
2. Program membuat pasangan kunci RSA 
3. Pesan dienkripsi dengan kunci publik RSA
4. Hash SHA-256 dihitung dari pesan asli
5. Header dibuat berisi hash dan kunci publik
6. File audio diproses dengan DWT
7. Bit dari header dan pesan disisipkan ke koefisien detail DWT
8. File audio dengan pesan tersembunyi disimpan

### Proses Ekstraksi (Extract)

1. Pengguna memberikan file audio yang berisi pesan tersembunyi
2. Program mengekstrak header untuk mendapatkan informasi hash dan kunci publik
3. Program mengekstrak bit pesan terenkripsi
4. Pesan didekripsi menggunakan kunci privat (dalam implementasi ini diasumsikan penerima memiliki kunci privat)
5. Hash dihitung ulang untuk memverifikasi integritas pesan 