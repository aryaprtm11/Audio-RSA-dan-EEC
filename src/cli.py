"""
Command-line interface untuk aplikasi steganografi audio dengan ECC dan RSA.
"""
from core import embed_message, extract_message, debug_extract

def main():
    """Fungsi utama CLI."""
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