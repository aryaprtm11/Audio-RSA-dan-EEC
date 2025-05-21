"""
GUI minimalis untuk aplikasi steganografi audio dengan ECC dan RSA
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import builtins

# Import modul steganografi audio
from core import embed_message, extract_message

class MinimalistSteganographyApp(tk.Tk):
    """GUI minimalis untuk steganografi audio dengan enkripsi ECC dan RSA"""
    
    def __init__(self):
        super().__init__()
        
        # Warna tema - monokromatik dengan aksen biru
        self.bg_color = "#ffffff"
        self.accent_color = "#1e88e5"  # Biru material
        self.text_color = "#212121"
        
        self.title("Steganografi Audio")
        self.geometry("650x520")
        self.minsize(600, 500)
        self.configure(bg=self.bg_color)
        
        # Variabel untuk proses yang sedang berjalan
        self.process_running = False
        
        # Buat direktori output jika belum ada
        os.makedirs('output', exist_ok=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Membuat elemen-elemen UI"""
        
        # Frame utama
        main_frame = tk.Frame(self, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Judul aplikasi
        title_label = tk.Label(
            main_frame, 
            text="AUDIO STEGANOGRAFI",
            font=("Segoe UI", 18),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 15))
        
        # Tab container
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Enkripsi
        self.encrypt_tab = tk.Frame(self.tab_control, bg=self.bg_color)
        self.tab_control.add(self.encrypt_tab, text="Enkripsi")
        self.create_encrypt_tab()
        
        # Tab 2: Dekripsi
        self.decrypt_tab = tk.Frame(self.tab_control, bg=self.bg_color)
        self.tab_control.add(self.decrypt_tab, text="Dekripsi")
        self.create_decrypt_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Siap")
        status_bar = tk.Label(
            self, 
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#f5f5f5",
            fg=self.text_color,
            font=("Segoe UI", 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_encrypt_tab(self):
        """Membuat tab enkripsi"""
        
        # Frame untuk form
        form_frame = tk.Frame(self.encrypt_tab, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input file
        tk.Label(
            form_frame, 
            text="File Audio:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.encrypt_input_var = tk.StringVar()
        input_frame = tk.Frame(form_frame, bg=self.bg_color)
        input_frame.grid(row=0, column=1, sticky=tk.EW, pady=(0, 5))
        
        input_entry = tk.Entry(
            input_frame, 
            textvariable=self.encrypt_input_var,
            width=40,
            font=("Segoe UI", 10)
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = tk.Button(
            input_frame, 
            text="Browse",
            command=self.browse_encrypt_input,
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            relief=tk.FLAT,
            padx=10
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Output file
        tk.Label(
            form_frame, 
            text="Output:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.encrypt_output_var = tk.StringVar()
        output_frame = tk.Frame(form_frame, bg=self.bg_color)
        output_frame.grid(row=1, column=1, sticky=tk.EW, pady=(0, 10))
        
        output_entry = tk.Entry(
            output_frame, 
            textvariable=self.encrypt_output_var,
            width=40,
            font=("Segoe UI", 10)
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_output = tk.Button(
            output_frame, 
            text="Browse",
            command=self.browse_encrypt_output,
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            relief=tk.FLAT,
            padx=10
        )
        browse_output.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Pesan
        tk.Label(
            form_frame, 
            text="Pesan:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, sticky=tk.NW, pady=(0, 10))
        
        self.encrypt_message = scrolledtext.ScrolledText(
            form_frame, 
            height=6, 
            width=40,
            font=("Segoe UI", 10)
        )
        self.encrypt_message.grid(row=2, column=1, sticky=tk.EW, pady=(0, 10))
        
        # Button
        button_frame = tk.Frame(form_frame, bg=self.bg_color)
        button_frame.grid(row=3, column=1, sticky=tk.E)
        
        encrypt_button = tk.Button(
            button_frame, 
            text="SISIPKAN PESAN",
            command=self.do_encrypt,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            font=("Segoe UI", 10, "bold")
        )
        encrypt_button.pack()
        
        # Log
        tk.Label(
            form_frame, 
            text="Log:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=4, column=0, sticky=tk.NW, pady=(10, 0))
        
        self.encrypt_log = scrolledtext.ScrolledText(
            form_frame, 
            height=4, 
            width=40,
            font=("Consolas", 9),
            bg="#f5f5f5"
        )
        self.encrypt_log.grid(row=4, column=1, sticky=tk.EW, pady=(10, 0))
        self.encrypt_log.config(state=tk.DISABLED)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
    
    def create_decrypt_tab(self):
        """Membuat tab dekripsi"""
        
        # Frame untuk form
        form_frame = tk.Frame(self.decrypt_tab, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input file
        tk.Label(
            form_frame, 
            text="File Stego:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.decrypt_input_var = tk.StringVar()
        input_frame = tk.Frame(form_frame, bg=self.bg_color)
        input_frame.grid(row=0, column=1, sticky=tk.EW, pady=(0, 10))
        
        input_entry = tk.Entry(
            input_frame, 
            textvariable=self.decrypt_input_var,
            width=40,
            font=("Segoe UI", 10)
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = tk.Button(
            input_frame, 
            text="Browse",
            command=self.browse_decrypt_input,
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            relief=tk.FLAT,
            padx=10
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Button
        button_frame = tk.Frame(form_frame, bg=self.bg_color)
        button_frame.grid(row=1, column=1, sticky=tk.E, pady=(0, 10))
        
        decrypt_button = tk.Button(
            button_frame, 
            text="EKSTRAK PESAN",
            command=self.do_decrypt,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            font=("Segoe UI", 10, "bold")
        )
        decrypt_button.pack()
        
        # Hasil
        tk.Label(
            form_frame, 
            text="Hasil:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, sticky=tk.NW, pady=(0, 10))
        
        self.decrypt_result = scrolledtext.ScrolledText(
            form_frame, 
            height=6, 
            width=40,
            font=("Segoe UI", 10)
        )
        self.decrypt_result.grid(row=2, column=1, sticky=tk.EW, pady=(0, 10))
        self.decrypt_result.config(state=tk.DISABLED)
        
        # Log
        tk.Label(
            form_frame, 
            text="Log:", 
            bg=self.bg_color, 
            fg=self.text_color,
            font=("Segoe UI", 10)
        ).grid(row=3, column=0, sticky=tk.NW, pady=(10, 0))
        
        self.decrypt_log = scrolledtext.ScrolledText(
            form_frame, 
            height=4, 
            width=40,
            font=("Consolas", 9),
            bg="#f5f5f5"
        )
        self.decrypt_log.grid(row=3, column=1, sticky=tk.EW, pady=(10, 0))
        self.decrypt_log.config(state=tk.DISABLED)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
    
    def browse_encrypt_input(self):
        """Memilih file audio input"""
        file_path = filedialog.askopenfilename(
            title="Pilih File Audio",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if file_path:
            self.encrypt_input_var.set(file_path)
            
            # Atur output path secara otomatis
            if not self.encrypt_output_var.get():
                basename = os.path.basename(file_path)
                name, ext = os.path.splitext(basename)
                self.encrypt_output_var.set(os.path.join('output', f"stego_{name}{ext}"))
    
    def browse_encrypt_output(self):
        """Memilih file output"""
        file_path = filedialog.asksaveasfilename(
            title="Simpan Sebagai",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            defaultextension=".wav",
            initialdir="output"
        )
        if file_path:
            self.encrypt_output_var.set(file_path)
    
    def browse_decrypt_input(self):
        """Memilih file stego input"""
        file_path = filedialog.askopenfilename(
            title="Pilih File Audio Stego",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if file_path:
            self.decrypt_input_var.set(file_path)
    
    def update_encrypt_log(self, text):
        """Update log enkripsi"""
        self.encrypt_log.config(state=tk.NORMAL)
        self.encrypt_log.insert(tk.END, f"{text}\n")
        self.encrypt_log.see(tk.END)
        self.encrypt_log.config(state=tk.DISABLED)
        self.update()
    
    def update_decrypt_log(self, text):
        """Update log dekripsi"""
        self.decrypt_log.config(state=tk.NORMAL)
        self.decrypt_log.insert(tk.END, f"{text}\n")
        self.decrypt_log.see(tk.END)
        self.decrypt_log.config(state=tk.DISABLED)
        self.update()
    
    def clear_encrypt_log(self):
        """Menghapus log enkripsi"""
        self.encrypt_log.config(state=tk.NORMAL)
        self.encrypt_log.delete(1.0, tk.END)
        self.encrypt_log.config(state=tk.DISABLED)
    
    def clear_decrypt_log(self):
        """Menghapus log dekripsi"""
        self.decrypt_log.config(state=tk.NORMAL)
        self.decrypt_log.delete(1.0, tk.END)
        self.decrypt_log.config(state=tk.DISABLED)
    
    def update_status(self, text):
        """Update status bar"""
        self.status_var.set(text)
        self.update()
    
    def do_encrypt(self):
        """Proses enkripsi"""
        if self.process_running:
            messagebox.showwarning("Proses Berjalan", "Mohon tunggu proses sebelumnya selesai")
            return
        
        input_file = self.encrypt_input_var.get().strip()
        output_file = self.encrypt_output_var.get().strip()
        message = self.encrypt_message.get(1.0, tk.END).strip()
        
        # Validasi
        if not input_file:
            messagebox.showerror("Error", "Silakan pilih file audio input")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"File '{input_file}' tidak ditemukan")
            return
        
        if not message:
            messagebox.showerror("Error", "Silakan masukkan pesan")
            return
        
        # Set output path default jika kosong
        if not output_file:
            basename = os.path.basename(input_file)
            name, ext = os.path.splitext(basename)
            output_file = os.path.join('output', f"stego_{name}{ext}")
            self.encrypt_output_var.set(output_file)
        
        # Reset log dan status
        self.clear_encrypt_log()
        self.update_status("Menyisipkan pesan...")
        self.process_running = True
        
        # Original print function
        original_print = builtins.print
        
        def encrypt_thread():
            try:
                # Custom print function for logging
                def custom_print(*args, sep=' ', end='\n', file=None, flush=False):
                    text = sep.join(map(str, args)) + end
                    self.after(10, lambda: self.update_encrypt_log(text.rstrip()))
                
                # Replace print
                builtins.print = custom_print
                
                # Run embed_message
                result = embed_message(input_file, output_file, message)
                
                # Restore print
                builtins.print = original_print
                
                if result:
                    self.after(10, lambda: self.update_status("Pesan berhasil disisipkan"))
                    self.after(10, lambda: messagebox.showinfo("Sukses", f"Pesan berhasil disisipkan ke:\n{result}"))
                else:
                    self.after(10, lambda: self.update_status("Gagal menyisipkan pesan"))
                    self.after(10, lambda: messagebox.showerror("Error", "Gagal menyisipkan pesan"))
            
            except Exception as e:
                # Restore print
                builtins.print = original_print
                
                self.after(10, lambda: self.update_status("Error"))
                self.after(10, lambda: self.update_encrypt_log(f"Error: {str(e)}"))
                self.after(10, lambda: messagebox.showerror("Error", str(e)))
            
            finally:
                # Ensure process_running is reset
                self.after(10, lambda: setattr(self, 'process_running', False))
        
        # Run in separate thread
        threading.Thread(target=encrypt_thread, daemon=True).start()
    
    def do_decrypt(self):
        """Proses dekripsi"""
        if self.process_running:
            messagebox.showwarning("Proses Berjalan", "Mohon tunggu proses sebelumnya selesai")
            return
        
        stego_file = self.decrypt_input_var.get().strip()
        
        # Validasi
        if not stego_file:
            messagebox.showerror("Error", "Silakan pilih file audio stego")
            return
        
        if not os.path.exists(stego_file):
            messagebox.showerror("Error", f"File '{stego_file}' tidak ditemukan")
            return
        
        # Reset result dan log
        self.decrypt_result.config(state=tk.NORMAL)
        self.decrypt_result.delete(1.0, tk.END)
        self.decrypt_result.config(state=tk.DISABLED)
        self.clear_decrypt_log()
        self.update_status("Mengekstrak pesan...")
        self.process_running = True
        
        # Original functions
        original_print = builtins.print
        original_input = builtins.input
        
        def decrypt_thread():
            try:
                # Custom print function for logging
                def custom_print(*args, sep=' ', end='\n', file=None, flush=False):
                    text = sep.join(map(str, args)) + end
                    self.after(10, lambda: self.update_decrypt_log(text.rstrip()))
                
                # Custom input function to auto-reply to prompts
                def custom_input(prompt=""):
                    return stego_file
                
                # Replace functions
                builtins.print = custom_print
                builtins.input = custom_input
                
                # Run extract_message
                extracted_message = extract_message(stego_file)
                
                # Restore functions
                builtins.print = original_print
                builtins.input = original_input
                
                # Update UI with result
                if extracted_message:
                    self.after(10, lambda: self.update_status("Pesan berhasil diekstrak"))
                    self.after(10, lambda: self.decrypt_result.config(state=tk.NORMAL))
                    self.after(10, lambda: self.decrypt_result.insert(tk.END, extracted_message))
                    self.after(10, lambda: self.decrypt_result.config(state=tk.DISABLED))
                    self.after(10, lambda: messagebox.showinfo("Sukses", "Pesan berhasil diekstrak"))
                else:
                    self.after(10, lambda: self.update_status("Gagal mengekstrak pesan"))
                    self.after(10, lambda: messagebox.showerror("Error", "Gagal mengekstrak pesan"))
            
            except Exception as e:
                # Restore functions
                builtins.print = original_print
                builtins.input = original_input
                
                self.after(10, lambda: self.update_status("Error"))
                self.after(10, lambda: self.update_decrypt_log(f"Error: {str(e)}"))
                self.after(10, lambda: messagebox.showerror("Error", str(e)))
            
            finally:
                # Ensure process_running is reset
                self.after(10, lambda: setattr(self, 'process_running', False))
        
        # Run in separate thread
        threading.Thread(target=decrypt_thread, daemon=True).start()

# Main function
def main():
    app = MinimalistSteganographyApp()
    
    # Buat hover effect untuk tombol
    for widget in app.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Notebook):
                    for tab in child.winfo_children():
                        for elem in tab.winfo_children():
                            if isinstance(elem, tk.Frame):
                                for component in elem.winfo_children():
                                    if isinstance(component, tk.Frame):
                                        for btn in component.winfo_children():
                                            if isinstance(btn, tk.Button) and btn['bg'] == app.accent_color:
                                                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1565C0"))
                                                btn.bind("<Leave>", lambda e, b=btn, a=app: b.config(bg=a.accent_color))
                                            elif isinstance(btn, tk.Button):
                                                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
                                                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#f0f0f0"))
    
    app.mainloop()

if __name__ == "__main__":
    main()