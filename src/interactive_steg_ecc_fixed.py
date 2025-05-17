"""
Steganografi audio interaktif yang menggunakan ECC dan DWT
Memungkinkan pengguna memasukkan pesan melalui terminal
"""
import os
import json
import base64
import numpy as np
import soundfile as sf
from dwt import AudioDWT
from ecc_simple import SimplifiedECCCrypto

def generate_audio(output_file, duration=10, sample_rate=44100):
    """Membuat file audio sampel dengan gelombang sinus sederhana."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(output_file, audio_data, sample_rate)
    print(f"File audio sampel dibuat: {output_file}")
    return output_file

def text_to_bits(text):
    """Konversi teks ke string bit."""
    bits = ""
    for char in text:
        bits += format(ord(char), '08b')  # Konversi karakter ke 8 bit
    return bits

def bits_to_text(bits):
    """Konversi string bit kembali ke teks."""
    text = ""
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte = bits[i:i+8]
            text += chr(int(byte, 2))
    return text

def bytes_to_bits(data):
    """Konversi bytes ke string bit."""
    bits = ""
    for byte in data:
        bits += format(byte, '08b')
    return bits

def bits_to_bytes(bits):
    """Konversi string bit ke bytes."""
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte = bits[i:i+8]
            bytes_data.append(int(byte, 2))
    return bytes(bytes_data)

def prepare_message(message, ecc_instance):
    """
    Menyiapkan pesan dengan enkripsi ECC
    """
    # Enkripsi pesan menggunakan ECC
    encrypted_data_base64, session_key_base64 = ecc_instance.encrypt_text(message)
    
    # Buat data header
    header = {
        "public_key": ecc_instance.get_public_key(),
        "message_length": len(message),
        "session_key": session_key_base64
    }
    
    # Serialisasi header dan data terenkripsi
    header_json = json.dumps(header)
    message_json = json.dumps(encrypted_data_base64)
    
    # Konversi ke data biner
    header_bits = text_to_bits(header_json)
    message_bits = text_to_bits(message_json)
    
    # Tambahkan panjang header (32 bit)
    header_length_bits = format(len(header_bits), '032b')
    
    # Gabungkan semua bit
    all_bits = header_length_bits + header_bits + message_bits
    
    return all_bits

def embed_message():
    """Menyisipkan pesan ke dalam file audio."""
    # Buat direktori output jika belum ada
    os.makedirs('output', exist_ok=True)
    
    # Tanya nama file audio atau gunakan default
    input_file = input("Masukkan path file audio asli (atau biarkan kosong untuk membuat file audio sampel): ").strip()
    
    if not input_file:
        input_file = 'output/ecc_sample.wav'
        generate_audio(input_file)
    elif not os.path.exists(input_file):
        print(f"File {input_file} tidak ditemukan. Membuat file audio sampel...")
        input_file = 'output/ecc_sample.wav'
        generate_audio(input_file)
    
    # Tanya nama file output
    output_file = input("Masukkan path file audio output (atau biarkan kosong untuk default): ").strip()
    if not output_file:
        output_file = 'output/ecc_stego.wav'
    
    # Tanya pesan yang akan disembunyikan
    message = input("Masukkan pesan yang akan disembunyikan: ")
    
    if not message:
        print("Pesan tidak boleh kosong")
        return
    
    # Buat instance ECC
    print("Membuat kunci ECC...")
    ecc = SimplifiedECCCrypto()
    print(f"Kunci ECC dibuat")
    
    # Siapkan pesan (enkripsi ECC)
    print("Menyiapkan pesan dengan enkripsi ECC...")
    all_bits = prepare_message(message, ecc)
    print(f"Pesan terenkripsi dengan panjang: {len(all_bits)} bit")
    
    # Buat instance DWT
    dwt = AudioDWT(wavelet='db2', level=1)
    
    # Cek kapasitas file audio
    audio_data, _ = dwt.read_audio(input_file)
    coeffs = dwt.apply_dwt(audio_data)
    capacity = len(coeffs[1])
    
    if len(all_bits) > capacity:
        print(f"Pesan terlalu panjang! Kapasitas maksimal: {capacity} bit, Pesan terenkripsi: {len(all_bits)} bit")
        return
    
    # Sembunyikan pesan dalam file audio
    print(f"\nMenyisipkan pesan ke dalam {output_file}...")
    success = dwt.embed_data(input_file, output_file, all_bits)
    
    if success:
        print(f"Pesan berhasil disembunyikan dalam file: {output_file}")
        
        # Buat file untuk menyimpan kunci
        key_file = output_file + ".key"
        with open(key_file, 'w') as f:
            f.write(f"PUBLIC KEY:\n{ecc.get_public_key()}\n")
            f.write(f"\nPRIVATE KEY:\n{ecc.get_private_key()}\n")
        print(f"Kunci ECC disimpan dalam {key_file}")
        
        # Tambahkan informasi panjang pesan dan kunci ke file info
        info_file = output_file + ".info"
        info = {
            "bits_length": len(all_bits),
            "public_key": ecc.get_public_key(),
            "private_key": ecc.get_private_key()
        }
        
        with open(info_file, 'w') as f:
            json.dump(info, f)
        print(f"Informasi panjang pesan dan kunci disimpan dalam {info_file}")
        print("PENTING: Dalam aplikasi nyata, kunci privat harus disimpan dengan aman!")

def extract_message():
    """Mengekstrak pesan dari file audio."""
    # Tanya nama file audio stego
    stego_file = input("Masukkan path file audio yang berisi pesan tersembunyi: ").strip()
    
    if not stego_file or not os.path.exists(stego_file):
        print("File tidak ditemukan")
        return
    
    # Cek apakah ada file info
    info_file = stego_file + ".info"
    private_key_str = None
    
    if os.path.exists(info_file):
        with open(info_file, 'r') as f:
            info = json.load(f)
        num_bits = info["bits_length"]
        private_key_str = info["private_key"]
        print(f"Mengekstrak {num_bits} bit dari file...")
    else:
        num_bits = int(input("Masukkan jumlah bit pesan yang akan diekstrak: "))
    
    # Cek juga file .key yang mungkin ada
    key_file = stego_file + ".key"
    if os.path.exists(key_file):
        print(f"File kunci ditemukan: {key_file}")
    
    # Buat instance DWT
    dwt = AudioDWT(wavelet='db2', level=1)
    
    try:
        # Ekstrak semua bit dari file audio
        print(f"\nMengekstrak pesan dari {stego_file}...")
        all_extracted_bits = dwt.extract_data(stego_file, num_bits)
        
        # Baca panjang header (32 bit pertama)
        header_length_bits = all_extracted_bits[:32]
        header_length = int(header_length_bits, 2)
        
        # Ekstrak header
        header_bits = all_extracted_bits[32:32+header_length]
        header_json = bits_to_text(header_bits)
        
        # Parse header
        header = json.loads(header_json)
        public_key_str = header["public_key"]
        message_length = header["message_length"]
        session_key_base64 = header["session_key"]
        
        # Ekstrak data terenkripsi
        message_bits = all_extracted_bits[32+header_length:]
        message_json = bits_to_text(message_bits)
        encrypted_data_base64 = json.loads(message_json)
        
        # Buat instance ECC
        ecc = SimplifiedECCCrypto()
        
        # Dekripsi pesan
        try:
            decrypted_message = ecc.decrypt_text(encrypted_data_base64, session_key_base64)
            print(f"\nPesan yang diekstrak: {decrypted_message}")
        except Exception as e:
            print(f"Gagal mendekripsi pesan: {str(e)}")
        
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekstrak pesan: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    while True:
        print("\n===== STEGANOGRAFI AUDIO DENGAN ECC DAN DWT =====")
        print("1. Sisipkan pesan ke dalam file audio")
        print("2. Ekstrak pesan dari file audio")
        print("3. Keluar")
        
        choice = input("\nPilih menu (1-3): ")
        
        if choice == '1':
            embed_message()
        elif choice == '2':
            extract_message()
        elif choice == '3':
            print("Terima kasih telah menggunakan program ini!")
            break
        else:
            print("Pilihan tidak valid. Silakan pilih 1-3.")

if __name__ == "__main__":
    main() 