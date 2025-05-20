import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from interactive_steg_ecc_fixed import embed_message, extract_message

class StegoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Audio Steganografi - ECC + DWT")
        self.geometry("400x300")

        tk.Label(self, text="Audio Steganografi dengan ECC + DWT", font=("Helvetica", 14)).pack(pady=20)

        tk.Button(self, text="🔐 Sisipkan Pesan", command=self.open_embed_window, width=30).pack(pady=10)
        tk.Button(self, text="🔓 Ekstrak Pesan", command=self.open_extract_window, width=30).pack(pady=10)
        tk.Button(self, text="❌ Keluar", command=self.destroy, width=30).pack(pady=10)

    def open_embed_window(self):
        EmbedWindow(self)

    def open_extract_window(self):
        ExtractWindow(self)


class EmbedWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sisipkan Pesan")
        self.geometry("400x300")

        tk.Label(self, text="File Audio Asli:").pack()
        self.audio_path = tk.Entry(self, width=50)
        self.audio_path.pack()
        tk.Button(self, text="Pilih File", command=self.browse_audio).pack()

        tk.Label(self, text="Pesan yang Disisipkan:").pack()
        self.message_entry = tk.Text(self, height=5)
        self.message_entry.pack()

        tk.Button(self, text="Sisipkan", command=self.run_embed).pack(pady=10)

    def browse_audio(self):
        file = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
        if file:
            self.audio_path.delete(0, tk.END)
            self.audio_path.insert(0, file)

    def run_embed(self):
        input_path = self.audio_path.get()
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Peringatan", "Pesan tidak boleh kosong")
            return

        # Jalankan proses di thread terpisah agar GUI tidak freeze
        threading.Thread(target=self.do_embed, args=(input_path, message), daemon=True).start()

    def do_embed(self, input_path, message):
        import builtins
        builtins.input = lambda prompt="": input_path if "audio asli" in prompt else (
            "output/stego_gui.wav" if "output" in prompt else message
        )
        embed_message()
        messagebox.showinfo("Sukses", "Pesan berhasil disisipkan!")


class ExtractWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ekstrak Pesan")
        self.geometry("400x250")

        tk.Label(self, text="File Audio Stego:").pack()
        self.audio_path = tk.Entry(self, width=50)
        self.audio_path.pack()
        tk.Button(self, text="Pilih File", command=self.browse_audio).pack()

        self.result_label = tk.Label(self, text="Pesan yang Diekstrak akan tampil di sini", wraplength=350)
        self.result_label.pack(pady=20)

        tk.Button(self, text="Ekstrak", command=self.run_extract).pack(pady=10)

    def browse_audio(self):
        file = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
        if file:
            self.audio_path.delete(0, tk.END)
            self.audio_path.insert(0, file)

    def run_extract(self):
        input_path = self.audio_path.get()

        # Jalankan proses di thread terpisah agar GUI tidak freeze
        threading.Thread(target=self.do_extract, args=(input_path,), daemon=True).start()

    def do_extract(self, input_path):
        import builtins
        builtins.input = lambda prompt="": input_path
        message = extract_message()
        self.result_label.config(text=f"Pesan yang diekstrak: {message}")



if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
