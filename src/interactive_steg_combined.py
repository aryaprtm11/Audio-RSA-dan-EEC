"""
Steganografi audio interaktif dengan kombinasi ECC dan RSA secara bersamaan
Menggunakan teknik DWT untuk menyembunyikan pesan yang telah dienkripsi dengan kedua algoritma
"""
import os
import json
import base64
import numpy as np
import soundfile as sf
from dwt import AudioDWT
from ecc_simple import SimplifiedECCCrypto
from rsa_simple import SimpleRSACrypto

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

def prepare_message(message):
    """
    Menyiapkan pesan dengan enkripsi ganda ECC kemudian RSA
    
    Args:
        message (str): Pesan yang akan dienkripsi
        
    Returns:
        tuple: (all_bits, ecc_crypto, rsa_crypto)
    """
    # Buat instance ECC
    print("Membuat kunci ECC...")
    ecc_crypto = SimplifiedECCCrypto()
    print("Kunci ECC dibuat")
    
    # Enkripsi pesan dengan ECC terlebih dahulu
    print("Menyiapkan enkripsi pertama dengan ECC...")
    ecc_encrypted_data_base64, ecc_key_base64 = ecc_crypto.encrypt_text(message)
    
    # Buat instance RSA
    print("Membuat kunci RSA (ini mungkin memakan waktu)...")
    rsa_crypto = SimpleRSACrypto()
    print("Kunci RSA dibuat")
    
    # Enkripsi hasil ECC dengan RSA
    print("Menyiapkan enkripsi kedua dengan RSA...")
    combined_message = json.dumps({
        "ecc_data": ecc_encrypted_data_base64,
        "ecc_key": ecc_key_base64
    })
    rsa_encrypted_data_base64, rsa_key_base64 = rsa_crypto.encrypt_text(combined_message)
    
    # Buat data header
    header = {
        "ecc_public_key": ecc_crypto.get_public_key(),
        "rsa_public_key": rsa_crypto.get_public_key(),
        "message_length": len(message),
        "rsa_key": rsa_key_base64
    }
    
    # Serialisasi header dan data terenkripsi
    header_json = json.dumps(header)
    message_json = json.dumps(rsa_encrypted_data_base64)
    
    # Konversi ke data biner
    header_bits = text_to_bits(header_json)
    message_bits = text_to_bits(message_json)
    
    # Tambahkan panjang header (32 bit)
    header_length_bits = format(len(header_bits), '032b')
    
    # Gabungkan semua bit
    all_bits = header_length_bits + header_bits + message_bits
    
    return all_bits, ecc_crypto, rsa_crypto

def embed_message():
    """Menyisipkan pesan ke dalam file audio."""
    # Buat direktori output jika belum ada
    os.makedirs('output', exist_ok=True)
    
    # Tanya nama file audio atau gunakan default
    input_file = input("Masukkan path file audio asli (atau biarkan kosong untuk membuat file audio sampel): ").strip()
    
    if not input_file:
        input_file = 'output/combined_sample.wav'
        generate_audio(input_file)
    elif not os.path.exists(input_file):
        print(f"File {input_file} tidak ditemukan. Membuat file audio sampel...")
        input_file = 'output/combined_sample.wav'
        generate_audio(input_file)
    
    # Tanya nama file output
    output_file = input("Masukkan path file audio output (atau biarkan kosong untuk default): ").strip()
    if not output_file:
        output_file = 'output/stego_combined.wav'
    
    # Tanya pesan yang akan disembunyikan
    message = input("Masukkan pesan yang akan disembunyikan: ")
    
    if not message:
        print("Pesan tidak boleh kosong")
        return
    
    # Tanya nilai alpha untuk DWT
    alpha_str = input("Masukkan nilai alpha untuk DWT (default 0.1): ").strip()
    alpha = 0.1  # nilai default
    if alpha_str:
        try:
            alpha = float(alpha_str)
            print(f"Menggunakan alpha = {alpha}")
        except ValueError:
            print(f"Nilai alpha tidak valid, menggunakan default 0.1")
    
    try:
        # Siapkan pesan dengan enkripsi ganda (ECC kemudian RSA)
        print("Menyiapkan pesan dengan enkripsi ganda ECC+RSA...")
        all_bits, ecc_crypto, rsa_crypto = prepare_message(message)
        print(f"Pesan terenkripsi dengan panjang: {len(all_bits)} bit")
        
        # Buat instance DWT
        dwt = AudioDWT(wavelet='db2', level=1)
        
        # Cek kapasitas file audio
        try:
            audio_data, _ = dwt.read_audio(input_file)
            coeffs = dwt.apply_dwt(audio_data)
            capacity = len(coeffs[1])
            
            if len(all_bits) > capacity:
                print(f"Pesan terlalu panjang! Kapasitas maksimal: {capacity} bit, Pesan terenkripsi: {len(all_bits)} bit")
                return
            
            # Sembunyikan pesan dalam file audio dengan nilai alpha yang ditentukan
            print(f"\nMenyisipkan pesan ke dalam {output_file}...")
            success = True
            
            # Terapkan DWT
            coeffs = dwt.apply_dwt(audio_data)
            
            # Sisipkan bit dengan alpha kustom
            modified_coeffs = dwt.embed_bits_in_coefficients(coeffs, all_bits, alpha=alpha)
            
            # Terapkan IDWT
            reconstructed_data = dwt.apply_idwt(modified_coeffs)
            
            # Jika audio original stereo, buat hasil rekonstruksi juga stereo
            if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                # Potong jika ukuran berbeda
                min_len = min(len(reconstructed_data), len(audio_data))
                reconstructed_stereo = np.zeros((min_len, audio_data.shape[1]))
                reconstructed_stereo[:, 0] = reconstructed_data[:min_len]
                # Salin channel lain dari audio asli
                for ch in range(1, audio_data.shape[1]):
                    reconstructed_stereo[:, ch] = audio_data[:min_len, ch]
                reconstructed_data = reconstructed_stereo
            
            # Simpan audio hasil
            dwt.save_audio(output_file, reconstructed_data, _)
            
            if success:
                print(f"Pesan berhasil disembunyikan dalam file: {output_file}")
                
                try:
                    # Buat file untuk menyimpan kunci
                    key_file = output_file + ".key"
                    with open(key_file, 'w') as f:
                        f.write("===== KUNCI ECC =====\n\n")
                        f.write(f"PUBLIC KEY ECC:\n{ecc_crypto.get_public_key()}\n\n")
                        f.write(f"PRIVATE KEY ECC:\n{ecc_crypto.get_private_key()}\n\n")
                        f.write("===== KUNCI RSA =====\n\n")
                        f.write(f"PUBLIC KEY RSA:\n{rsa_crypto.get_public_key()}\n\n")
                        f.write(f"PRIVATE KEY RSA:\n{rsa_crypto.get_private_key()}\n")
                    print(f"Kunci ECC dan RSA disimpan dalam {key_file}")
                    
                    # Tambahkan informasi panjang pesan dan kunci ke file info
                    info_file = output_file + ".info"
                    info = {
                        "bits_length": len(all_bits),
                        "ecc_public_key": ecc_crypto.get_public_key(),
                        "ecc_private_key": ecc_crypto.get_private_key(),
                        "rsa_public_key": rsa_crypto.get_public_key(),
                        "rsa_private_key": rsa_crypto.get_private_key(),
                        "message_length": len(message),
                        "alpha": alpha  # Simpan nilai alpha yang digunakan
                    }
                    
                    with open(info_file, 'w') as f:
                        json.dump(info, f)
                    print(f"Informasi panjang pesan dan kunci disimpan dalam {info_file}")
                    print("PENTING: Dalam aplikasi nyata, kunci privat harus disimpan dengan aman!")
                except Exception as e:
                    print(f"Peringatan: Terjadi masalah saat menyimpan file kunci: {str(e)}")
                    print("Pesan tetap tersimpan dalam file audio, tetapi kunci mungkin tidak tersimpan dengan benar.")
        except Exception as e:
            print(f"Error saat mengakses atau memproses file audio: {str(e)}")
    except Exception as e:
        print(f"Terjadi kesalahan saat menyiapkan pesan: {str(e)}")
        import traceback
        traceback.print_exc()

def extract_message():
    """Mengekstrak pesan dari file audio."""
    # Tanya nama file audio stego
    stego_file = input("Masukkan path file audio yang berisi pesan tersembunyi: ").strip()
    
    if not stego_file or not os.path.exists(stego_file):
        print("File tidak ditemukan")
        return None
    
    # Cek apakah ada file info
    info_file = stego_file + ".info"
    ecc_private_key = None
    rsa_private_key = None
    alpha = 0.1  # Default alpha
    
    if os.path.exists(info_file):
        try:
            with open(info_file, 'r') as f:
                info = json.load(f)
            num_bits = info["bits_length"]
            ecc_private_key = info.get("ecc_private_key")
            rsa_private_key = info.get("rsa_private_key")
            
            # Ambil nilai alpha jika tersedia
            if "alpha" in info:
                alpha = info["alpha"]
                print(f"Menggunakan nilai alpha dari file info: {alpha}")
            else:
                print(f"Nilai alpha tidak ditemukan di file info, menggunakan default: {alpha}")
                
            print(f"Mengekstrak {num_bits} bit dari file...")
        except json.JSONDecodeError:
            print("File info tidak valid. Mohon masukkan jumlah bit secara manual.")
            num_bits = int(input("Masukkan jumlah bit pesan yang akan diekstrak: "))
            
            # Tanya nilai alpha jika file info tidak valid
            alpha_str = input("Masukkan nilai alpha untuk DWT (default 0.1): ").strip()
            if alpha_str:
                try:
                    alpha = float(alpha_str)
                    print(f"Menggunakan alpha = {alpha}")
                except ValueError:
                    print(f"Nilai alpha tidak valid, menggunakan default 0.1")
    else:
        num_bits = int(input("Masukkan jumlah bit pesan yang akan diekstrak: "))
        
        # Tanya nilai alpha jika tidak ada file info
        alpha_str = input("Masukkan nilai alpha untuk DWT (default 0.1): ").strip()
        if alpha_str:
            try:
                alpha = float(alpha_str)
                print(f"Menggunakan alpha = {alpha}")
            except ValueError:
                print(f"Nilai alpha tidak valid, menggunakan default 0.1")
    
    # Cek juga file .key yang mungkin ada
    key_file = stego_file + ".key"
    if os.path.exists(key_file):
        print(f"File kunci ditemukan: {key_file}")
    
    # Buat instance DWT
    dwt = AudioDWT(wavelet='db2', level=1)
    
    try:
        # Ekstrak semua bit dari file audio
        print(f"\nMengekstrak pesan dari {stego_file}...")
        
        # Baca file audio stego
        stego_data, sample_rate = dwt.read_audio(stego_file)
        
        # Terapkan DWT
        coeffs = dwt.apply_dwt(stego_data)
        
        # Ekstrak bit dengan nilai alpha yang diberikan
        all_extracted_bits = dwt.extract_bits_from_coefficients(coeffs, num_bits, alpha=alpha)
        
        if len(all_extracted_bits) < 32:
            print("Data yang diekstrak terlalu pendek! Tidak bisa membaca header.")
            return None
        
        # Baca panjang header (32 bit pertama)
        header_length_bits = all_extracted_bits[:32]
        try:
            header_length = int(header_length_bits, 2)
        except ValueError:
            print(f"Error: Bit header panjang tidak valid: {header_length_bits}")
            return None
        
        # Pastikan data cukup panjang
        if len(all_extracted_bits) < 32 + header_length:
            print("Data yang diekstrak tidak lengkap! Header tidak lengkap.")
            return None
        
        # Ekstrak header
        header_bits = all_extracted_bits[32:32+header_length]
        header_json = bits_to_text(header_bits)
        
        try:
            # Parse header
            header = json.loads(header_json)
            ecc_public_key = header["ecc_public_key"]
            rsa_public_key = header["rsa_public_key"]
            message_length = header["message_length"]
            rsa_key_base64 = header["rsa_key"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error saat parsing header: {str(e)}")
            print(f"Header JSON: {header_json[:100]}...")  # Hanya tampilkan sebagian
            return None
        
        # Pastikan data cukup panjang untuk pesan
        if len(all_extracted_bits) < 32 + header_length + 8:  # minimal 1 byte pesan
            print("Data yang diekstrak tidak lengkap! Pesan tidak ditemukan.")
            return None
        
        # Ekstrak data terenkripsi
        message_bits = all_extracted_bits[32+header_length:]
        message_json = bits_to_text(message_bits)
        
        try:
            rsa_encrypted_data_base64 = json.loads(message_json)
        except json.JSONDecodeError:
            print(f"Error saat parsing pesan terenkripsi. Data mungkin rusak.")
            print(f"Data terenkripsi: {message_json[:100]}...")  # Hanya tampilkan sebagian
            return None
        
        # Dekripsi dengan RSA terlebih dahulu
        rsa_crypto = SimpleRSACrypto()
        
        # Load kunci RSA jika tersedia
        if rsa_private_key:
            print("Mencoba memuat kunci RSA yang tersimpan...")
            if rsa_crypto.load_key(rsa_private_key):
                print("Kunci RSA berhasil dimuat!")
        
        try:
            # Dekripsi layer pertama (RSA)
            print("Mencoba mendekripsi dengan RSA...")
            combined_message = rsa_crypto.decrypt_text(rsa_encrypted_data_base64, rsa_key_base64)
            
            try:
                combined_data = json.loads(combined_message)
                
                ecc_encrypted_data_base64 = combined_data["ecc_data"]
                ecc_key_base64 = combined_data["ecc_key"]
                
                # Buat instance ECC
                ecc_crypto = SimplifiedECCCrypto()
                
                # Load kunci ECC jika tersedia
                if ecc_private_key:
                    print("Mencoba memuat kunci ECC yang tersimpan...")
                    if ecc_crypto.load_key(ecc_private_key):
                        print("Kunci ECC berhasil dimuat!")
                
                # Dekripsi layer kedua (ECC)
                print("Mencoba mendekripsi dengan ECC...")
                decrypted_message = ecc_crypto.decrypt_text(ecc_encrypted_data_base64, ecc_key_base64)
                print(f"\nPesan yang diekstrak: {decrypted_message}")
                
                return decrypted_message
                
            except json.JSONDecodeError:
                print(f"Error saat parsing data ECC. Data RSA terdekripsi tetapi format tidak valid.")
                print(f"Data hasil dekripsi RSA: {combined_message[:100]}...")
                return None
            except KeyError as e:
                print(f"Kunci tidak ditemukan dalam data ECC: {str(e)}")
                return None
            
        except Exception as e:
            print(f"Gagal mendekripsi pesan pada layer RSA: {str(e)}")
            print("Kemungkinan alasannya: kunci privat RSA tidak cocok atau data rusak")
            return None
        
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekstrak pesan: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def debug_extract():
    """Fungsi debug untuk mengekstrak dan menampilkan data mentah."""
    # Tanya nama file audio stego
    stego_file = input("Masukkan path file audio yang akan di-debug: ").strip()
    
    if not stego_file or not os.path.exists(stego_file):
        print("File tidak ditemukan")
        return
    
    # Cek apakah ada file info
    info_file = stego_file + ".info"
    if os.path.exists(info_file):
        try:
            with open(info_file, 'r') as f:
                info = json.load(f)
            num_bits = info["bits_length"]
            print(f"Jumlah bit dari file info: {num_bits}")
        except Exception as e:
            print(f"Error membaca file info: {str(e)}")
            num_bits = int(input("Masukkan jumlah bit yang akan diekstrak untuk debug: "))
    else:
        num_bits = int(input("Masukkan jumlah bit yang akan diekstrak untuk debug: "))
    
    # Buat instance DWT
    dwt = AudioDWT(wavelet='db2', level=1)
    
    try:
        # Ekstrak bit dari file audio
        print(f"Mengekstrak {num_bits} bit dari file...")
        all_extracted_bits = dwt.extract_data(stego_file, num_bits)
        
        print(f"Jumlah bit yang berhasil diekstrak: {len(all_extracted_bits)}")
        
        if len(all_extracted_bits) < 32:
            print("ERROR: Data terlalu pendek! Minimal 32 bit diperlukan untuk header.")
            return
        
        # Baca panjang header
        header_length_bits = all_extracted_bits[:32]
        try:
            header_length = int(header_length_bits, 2)
            print(f"Panjang header: {header_length} bit")
        except ValueError:
            print(f"ERROR: Bit header panjang tidak valid: {header_length_bits}")
            return
        
        # Cek panjang data
        if len(all_extracted_bits) < 32 + header_length:
            print(f"ERROR: Data terlalu pendek! Butuh {32 + header_length} bit, hanya ada {len(all_extracted_bits)} bit.")
            return
        
        # Ekstrak header
        header_bits = all_extracted_bits[32:32+header_length]
        header_text = bits_to_text(header_bits)
        
        print("\n===== HEADER TERekstrak (3 baris pertama) =====")
        header_lines = header_text.split('\n')
        for i in range(min(3, len(header_lines))):
            print(header_lines[i])
        
        try:
            header = json.loads(header_text)
            print("\n===== HEADER DIPARSE DENGAN SUKSES =====")
            print(f"Message length: {header.get('message_length', 'N/A')}")
            if 'ecc_public_key' in header:
                print("ECC public key tersedia")
            if 'rsa_public_key' in header:
                print("RSA public key tersedia")
            if 'rsa_key' in header:
                print("RSA session key tersedia")
        except json.JSONDecodeError as e:
            print(f"\nERROR: Gagal mem-parse header JSON: {str(e)}")
            print(f"Header JSON raw: {header_text[:100]}...")
        
        # Ekstrak message
        if len(all_extracted_bits) <= 32 + header_length:
            print("ERROR: Tidak ada data pesan!")
            return
        
        message_bits = all_extracted_bits[32+header_length:]
        message_text = bits_to_text(message_bits)
        
        print("\n===== PESAN TERENKRIPSI (awal) =====")
        print(message_text[:100] + "..." if len(message_text) > 100 else message_text)
        
        try:
            message_json = json.loads(message_text)
            print("\n===== PESAN BERHASIL DIPARSE =====")
            print("Pesan dalam format JSON yang valid")
        except json.JSONDecodeError as e:
            print(f"\nERROR: Gagal mem-parse pesan JSON: {str(e)}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    while True:
        print("\n===== STEGANOGRAFI AUDIO DENGAN ENKRIPSI GANDA ECC+RSA DAN DWT =====")
        print("1. Sisipkan pesan ke dalam file audio")
        print("2. Ekstrak pesan dari file audio")
        print("3. Debug ekstraksi")
        print("4. Keluar")
        
        choice = input("\nPilih menu (1-4): ")
        
        if choice == '1':
            embed_message()
        elif choice == '2':
            extract_message()
        elif choice == '3':
            debug_extract()
        elif choice == '4':
            print("Terima kasih telah menggunakan program ini!")
            break
        else:
            print("Pilihan tidak valid. Silakan pilih 1-4.")

if __name__ == "__main__":
    main() 