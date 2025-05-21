import time
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from datetime import datetime
import json

# Add the parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import actual encryption modules
from crypto.ecc import SimplifiedECCCrypto
from crypto.rsa import SimpleRSACrypto
from core import prepare_message
from utils.bit_utils import text_to_bits, bits_to_text

# Reuse the same encryption/decryption functions
def encrypt_message(plaintext):
    """Encrypt a message using the actual ECC+RSA encryption"""
    all_bits, ecc_crypto, rsa_crypto = prepare_message(plaintext)
    encrypted_data = {
        'all_bits': all_bits,
        'ecc_private_key': ecc_crypto.get_private_key(),
        'rsa_private_key': rsa_crypto.get_private_key()
    }
    return encrypted_data

def decrypt_message(encrypted_data):
    """Decrypt a message using the actual ECC+RSA decryption"""
    all_bits = encrypted_data['all_bits']
    
    # Extract header length
    header_length_bits = all_bits[:32]
    header_length = int(header_length_bits, 2)
    
    # Extract header
    header_bits = all_bits[32:32+header_length]
    header_json = bits_to_text(header_bits)
    header = json.loads(header_json)
    
    # Extract message
    message_bits = all_bits[32+header_length:]
    message_json = bits_to_text(message_bits)
    rsa_encrypted_data_base64 = json.loads(message_json)
    
    # Decrypt with RSA
    rsa_crypto = SimpleRSACrypto()
    rsa_crypto.load_key(encrypted_data['rsa_private_key'])
    rsa_key_base64 = header["rsa_key"]
    combined_message = rsa_crypto.decrypt_text(rsa_encrypted_data_base64, rsa_key_base64)
    
    # Decrypt with ECC
    combined_data = json.loads(combined_message)
    ecc_encrypted_data_base64 = combined_data["ecc_data"]
    ecc_key_base64 = combined_data["ecc_key"]
    
    ecc_crypto = SimplifiedECCCrypto()
    ecc_crypto.load_key(encrypted_data['ecc_private_key'])
    decrypted_message = ecc_crypto.decrypt_text(ecc_encrypted_data_base64, ecc_key_base64)
    
    return decrypted_message

def run_simple_benchmark():
    """Run a simple benchmark with 5 runs for each message length"""
    # Create output directory
    output_dir = "src/evaluations/output/time_performance"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test parameters
    message_lengths = [10, 50, 100, 200, 500]
    num_runs = 5  # Jalankan 5 kali untuk setiap ukuran pesan
    
    # Untuk menyimpan waktu rata-rata
    avg_enc_times = []
    avg_dec_times = []
    
    print("===== ECC+RSA ENCRYPTION PERFORMANCE TEST =====")
    print(f"Running {num_runs} iterations for each message length")
    
    # Uji setiap ukuran pesan
    for length in message_lengths:
        print(f"\n--- Testing with {length} characters ---")
        
        enc_times = []
        dec_times = []
        
        # Lakukan 5 kali pengujian
        for run in range(1, num_runs + 1):
            # Buat pesan uji dengan panjang tertentu
            test_message = "A" * length
            
            # Ukur waktu enkripsi
            start_time = time.time()
            encrypted = encrypt_message(test_message)
            enc_time = time.time() - start_time
            enc_times.append(enc_time)
            
            # Ukur waktu dekripsi
            start_time = time.time()
            decrypted = decrypt_message(encrypted)
            dec_time = time.time() - start_time
            dec_times.append(dec_time)
            
            print(f"  Run {run}: Enc: {enc_time:.4f}s, Dec: {dec_time:.4f}s")
            
            # Verifikasi dekripsi berhasil
            assert decrypted == test_message
            
            # Pause sejenak
            time.sleep(0.2)
        
        # Hitung rata-rata
        avg_enc = np.mean(enc_times)
        avg_dec = np.mean(dec_times)
        
        avg_enc_times.append(avg_enc)
        avg_dec_times.append(avg_dec)
        
        print(f"  Average: Enc: {avg_enc:.4f}s, Dec: {avg_dec:.4f}s")
    
    # Buat grafik batang sederhana
    plt.figure(figsize=(12, 8))
    
    x = np.arange(len(message_lengths))
    width = 0.35
    
    plt.bar(x - width/2, avg_enc_times, width, label='Enkripsi')
    plt.bar(x + width/2, avg_dec_times, width, label='Dekripsi')
    
    plt.xlabel('Panjang Pesan (karakter)')
    plt.ylabel('Waktu Rata-rata (detik)')
    plt.title('Performa Enkripsi dan Dekripsi ECC+RSA')
    plt.xticks(x, message_lengths)
    plt.legend()
    
    # Tambahkan label nilai pada grafik batang
    for i, v in enumerate(avg_enc_times):
        plt.text(i - width/2, v + 0.01, f'{v:.4f}s', ha='center')
        
    for i, v in enumerate(avg_dec_times):
        plt.text(i + width/2, v + 0.01, f'{v:.4f}s', ha='center')
        
    plt.grid(axis='y', alpha=0.3)
    
    # Tambahkan catatan penjelasan
    plt.figtext(0.5, 0.01,
               "Catatan: Hasil menunjukkan waktu rata-rata dari 5 kali pengujian untuk setiap ukuran pesan.\n"
               "Waktu enkripsi/dekripsi tidak selalu naik secara linear karena overhead tetap (inisialisasi dan pembuatan kunci).",
               ha='center', fontsize=10, bbox=dict(facecolor='lightyellow', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.07, 1, 1])
    
    # Simpan grafik
    save_path = f"{output_dir}/performance_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(save_path)
    print(f"\nGrafik hasil tersimpan di: {save_path}")
    
    plt.show()

# Jalankan benchmark
if __name__ == "__main__":
    run_simple_benchmark()