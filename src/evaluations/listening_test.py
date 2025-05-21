import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sounddevice as sd
import soundfile as sf
import threading
import os
import json
import datetime
from typing import List, Dict, Tuple, Any, Optional

class ListeningTestApp:
    def __init__(self, root: tk.Tk):
        """Initialize the listening test application."""
        self.root = root
        self.root.title("Audio Steganography Listening Test")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        
        # Create output directory
        self.output_dir = "src/evaluations/output/listening_test"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test configuration
        self.test_name = "Stego Audio Quality Assessment"
        self.test_description = "Compare original and processed audio files"
        self.current_trial = 0
        self.total_trials = 1  # Just one pair to test
        
        # Predefined audio files
        self.default_original = "input/test_crypto.wav"
        self.default_stego = "output/stego_test_crypto.wav"
        
        # Audio data
        self.original_file = self.default_original
        self.stego_file = self.default_stego
        self.paired_files = [(self.original_file, self.stego_file)]
        self.current_playing = None  # Track currently playing audio
        self.audio_data = {}  # Cache for loaded audio files
        self.audio_thread = None
        self.stop_playback = False
        
        # Randomize which is A and which is B
        self.ab_mapping = []
        if np.random.random() > 0.5:
            self.ab_mapping.append(('original', 'stego'))  # Original is A, Stego is B
        else:
            self.ab_mapping.append(('stego', 'original'))  # Stego is A, Original is B
        
        # Results storage
        self.results = []
        
        # Create UI
        self._create_ui()
        
        # Check if files exist
        if not os.path.exists(self.original_file) or not os.path.exists(self.stego_file):
            messagebox.showwarning("File Not Found", 
                                  f"One or both audio files not found:\n"
                                  f"Original: {self.original_file}\n"
                                  f"Stego: {self.stego_file}")
        
    def _create_ui(self):
        """Create the user interface."""
        # Main layout frames
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tab control with test interface and results tabs
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # First tab: Test interface
        self.test_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.test_tab, text='Listening Test')
        
        # Second tab: Results
        self.results_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.results_tab, text='Results')
        
        self.tab_control.pack(expand=True, fill=tk.BOTH)
        
        # Test tab content
        self._create_test_tab()
        
        # Results tab content
        self._create_results_tab()
        
        # Initially disable the results tab
        self.tab_control.tab(1, state='disabled')
        
    def _create_test_tab(self):
        """Create content for the listening test tab."""
        test_frame = ttk.Frame(self.test_tab, padding=10)
        test_frame.pack(fill=tk.BOTH, expand=True)
        
        # Information frame
        info_frame = ttk.LabelFrame(test_frame, text="Test Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="This test compares the audio quality between the original and stego audio samples.").pack(pady=5)
        ttk.Label(info_frame, text="Play both Sample A and Sample B, then rate which one has better quality.").pack(pady=5)
        
        # Files being compared
        files_frame = ttk.Frame(info_frame)
        files_frame.pack(fill=tk.X, pady=5)
        ttk.Label(files_frame, text="Original file: ").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(files_frame, text=self.original_file).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(files_frame, text="Stego file: ").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(files_frame, text=self.stego_file).grid(row=1, column=1, sticky=tk.W)
        
        # Playback controls
        playback_frame = ttk.LabelFrame(test_frame, text="Audio Playback", padding=10)
        playback_frame.pack(fill=tk.X, pady=10)
        
        # A/B buttons for blind testing
        self.button_A = ttk.Button(playback_frame, text="Play Sample A", width=20,
                                  command=lambda: self._play_sample('A'))
        self.button_A.grid(row=0, column=0, padx=10, pady=10)
        
        self.button_B = ttk.Button(playback_frame, text="Play Sample B", width=20,
                                  command=lambda: self._play_sample('B'))
        self.button_B.grid(row=0, column=1, padx=10, pady=10)
        
        self.stop_button = ttk.Button(playback_frame, text="Stop Playback", width=20,
                                     command=self._stop_playback)
        self.stop_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Rating controls
        rating_frame = ttk.LabelFrame(test_frame, text="Quality Assessment", padding=10)
        rating_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(rating_frame, text="Which sample has better audio quality?").pack(pady=5)
        
        self.rating_var = tk.StringVar()
        self.rating_scale = tk.IntVar()
        
        # Radio buttons for A/B selection
        selection_frame = ttk.Frame(rating_frame)
        selection_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(selection_frame, text="Sample A is better", variable=self.rating_var, value="A").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(selection_frame, text="Both are equal", variable=self.rating_var, value="Equal").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(selection_frame, text="Sample B is better", variable=self.rating_var, value="B").pack(side=tk.LEFT, padx=20)
        
        # Scale for quality difference
        scale_frame = ttk.LabelFrame(rating_frame, text="Rate the difference in quality")
        scale_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(scale_frame, text="No difference").pack(side=tk.LEFT, padx=10)
        self.quality_scale = ttk.Scale(scale_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                                      variable=self.rating_scale, length=300)
        self.quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(scale_frame, text="Very different").pack(side=tk.LEFT, padx=10)
        
        # Comments
        ttk.Label(rating_frame, text="Comments/Observations:").pack(anchor=tk.W, pady=5)
        self.comments_text = tk.Text(rating_frame, height=3, width=40)
        self.comments_text.pack(fill=tk.X, pady=5)
        
        # Finish button
        self.finish_button = ttk.Button(test_frame, text="Complete Test",
                                      command=self._finish_test)
        self.finish_button.pack(pady=20)
        
    def _create_results_tab(self):
        """Create content for the results tab."""
        results_frame = ttk.Frame(self.results_tab, padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary statistics
        summary_frame = ttk.LabelFrame(results_frame, text="Test Results Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=10, width=60)
        self.summary_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Results visualization
        viz_frame = ttk.LabelFrame(results_frame, text="Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a figure for matplotlib plots
        self.fig = plt.Figure(figsize=(9, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(export_frame, text="Export Results...", 
                  command=self._export_results).pack(side=tk.LEFT, padx=5)
                  
        ttk.Button(export_frame, text="Export Chart...", 
                  command=self._export_chart).pack(side=tk.LEFT, padx=5)
    
    def _play_sample(self, sample_id: str):
        """Play the selected audio sample (A or B)."""
        self._stop_playback()  # Stop any currently playing audio
        
        # Get the current pair of files
        original_file, stego_file = self.paired_files[0]
        
        # Determine which file to play based on A/B mapping
        ab_map = self.ab_mapping[0]
        if sample_id == 'A':
            file_to_play = original_file if ab_map[0] == 'original' else stego_file
        else:  # sample_id == 'B'
            file_to_play = stego_file if ab_map[1] == 'stego' else original_file
        
        # Start playback in a separate thread
        self.current_playing = sample_id
        self.stop_playback = False
        self.audio_thread = threading.Thread(target=self._play_audio, args=(file_to_play, sample_id))
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def _play_audio(self, file_path: str, sample_id: str):
        """Play audio file (runs in a separate thread)."""
        try:
            # Load the audio file if not already in cache
            if file_path not in self.audio_data:
                data, sample_rate = sf.read(file_path)
                self.audio_data[file_path] = (data, sample_rate)
            else:
                data, sample_rate = self.audio_data[file_path]
            
            # Play the audio
            sd.play(data, sample_rate)
            sd.wait()  # Wait until audio playback is done
        except Exception as e:
            messagebox.showerror("Playback Error", f"Error playing {sample_id}: {str(e)}")
            self.current_playing = None
    
    def _stop_playback(self):
        """Stop any currently playing audio."""
        if self.audio_thread and self.audio_thread.is_alive():
            self.stop_playback = True
            sd.stop()
            self.audio_thread.join(timeout=1.0)
        self.current_playing = None
    
    def _finish_test(self):
        """Complete the test and show results."""
        # Check if a rating was selected
        if not self.rating_var.get():
            messagebox.showwarning("Missing Rating", "Please select which sample has better quality.")
            return
        
        # Save results
        result = {
            'trial': 1,
            'original_file': self.original_file,
            'stego_file': self.stego_file,
            'ab_mapping': self.ab_mapping[0],
            'rating': self.rating_var.get(),
            'difference_scale': self.rating_scale.get(),
            'comments': self.comments_text.get(1.0, tk.END).strip()
        }
        
        self.results = [result]  # Single result
        
        # Process and display results
        self._process_results()
        
        # Enable results tab and switch to it
        self.tab_control.tab(1, state='normal')
        self.tab_control.select(1)
        
        # Auto-export results
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self._export_results(f"{self.output_dir}/listening_test_results_{timestamp}.json")
        self._export_chart(f"{self.output_dir}/listening_test_chart_{timestamp}.png")
    
    def _process_results(self):
        """Process test results and update the results tab."""
        if not self.results:
            messagebox.showerror("Error", "No results to process")
            return
        
        # Get the result
        result = self.results[0]
        
        # Determine preferences
        original_preference = 0
        stego_preference = 0
        no_preference = 0
        
        ab_map = result['ab_mapping']
        rating = result['rating']
        
        if rating == 'A':
            if ab_map[0] == 'original':
                original_preference = 1
            else:
                stego_preference = 1
        elif rating == 'B':
            if ab_map[1] == 'original':
                original_preference = 1
            else:
                stego_preference = 1
        else:  # Equal
            no_preference = 1
        
        # Check if participant correctly identified the original vs. stego
        correct_identification = 0
        orig_is_better = False
        if rating == 'A' and ab_map[0] == 'original':
            orig_is_better = True
        elif rating == 'B' and ab_map[1] == 'original':
            orig_is_better = True
            
        if orig_is_better or rating == 'Equal':
            correct_identification = 1
            
        # Update summary text
        summary = f"Test Name: {self.test_name}\n"
        summary += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        summary += f"Original Audio Preferred: {'Yes' if original_preference==1 else 'No'}\n"
        summary += f"Stego Audio Preferred: {'Yes' if stego_preference==1 else 'No'}\n"
        summary += f"No Preference: {'Yes' if no_preference==1 else 'No'}\n\n"
        summary += f"Perceived Difference Level: {result['difference_scale']}/5\n\n"
        
        # Interpretation
        if original_preference == 1:
            summary += "Interpretation: Original audio was perceived as better quality."
            if result['difference_scale'] <= 2:
                summary += "\nHowever, the difference was rated as small."
            else:
                summary += "\nThe difference was rated as significant."
        elif stego_preference == 1:
            summary += "Interpretation: Stego audio was perceived as better quality (unusual)."
            if result['difference_scale'] <= 2:
                summary += "\nHowever, the difference was rated as small."
            else:
                summary += "\nThe difference was rated as significant."
        else:
            summary += "Interpretation: No quality difference was perceived between original and stego audio.\n"
            summary += "This suggests excellent steganographic quality."
        
        # Add comments
        if result['comments']:
            summary += f"\n\nUser Comments:\n{result['comments']}"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        
        # Create visualization
        self._create_results_charts(original_preference, stego_preference, no_preference, result['difference_scale'])
    
    def _create_results_charts(self, original_pref: int, stego_pref: int, equal_pref: int, difference_rating: int):
        """Create charts to visualize results."""
        self.fig.clear()
        
        # Create subplots
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        
        # Pie chart of preferences
        labels = ['Original Better', 'Equal', 'Stego Better']
        sizes = [original_pref, equal_pref, stego_pref]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        # Determine which option was selected
        result_text = ""
        result_color = ""
        
        if original_pref == 1:
            result_text = "Original Audio\nPerceived Better"
            result_color = colors[0]
        elif equal_pref == 1:
            result_text = "No Difference\nDetected"
            result_color = colors[1]
        else:  # stego_pref == 1
            result_text = "Stego Audio\nPerceived Better"
            result_color = colors[2]
        
        # Create pie with single slice (no need for multiple slices when only one can be selected)
        ax1.pie([1], colors=[result_color], shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Add text in the center of the pie
        ax1.text(0, 0, result_text, ha='center', va='center', 
                 fontweight='bold', fontsize=12)
        
        ax1.set_title('Audio Quality Assessment')
        
        # Bar chart for quality difference rating
        x = ['No\ndifference', 'Very\nslight', 'Slight', 'Noticeable', 'Strong', 'Very\nstrong']
        ratings = [1 if i == difference_rating else 0 for i in range(6)]
        
        ax2.bar(x, ratings, color='skyblue')
        ax2.set_xlabel('Perceived Difference Rating')
        ax2.set_ylabel('Selection')
        ax2.set_title('Quality Difference Level')
        ax2.set_ylim(0, 1.2)  # Set y limit to make bar clearly visible
        
        # Add rating label above the selected bar
        for i, v in enumerate(ratings):
            if v > 0:
                ax2.text(i, v + 0.1, 'Selected', ha='center')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _export_results(self, file_path=None):
        """Export results to a JSON file."""
        if not self.results:
            messagebox.showerror("Error", "No results to export")
            return
        
        if file_path is None:    
            file_path = filedialog.asksaveasfilename(
                title="Export Results",
                initialdir=self.output_dir,
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
                defaultextension=".json"
            )
        
        if file_path:
            # Make sure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create exportable data structure
            export_data = {
                'test_name': self.test_name,
                'test_description': self.test_description,
                'date': datetime.datetime.now().isoformat(),
                'original_file': os.path.basename(self.original_file),
                'stego_file': os.path.basename(self.stego_file),
                'ab_mapping': self.ab_mapping[0],
                'rating': self.results[0]['rating'],
                'difference_scale': self.results[0]['difference_scale'],
                'comments': self.results[0]['comments']
            }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            messagebox.showinfo("Export Complete", f"Results exported to {file_path}")
    
    def _export_chart(self, file_path=None):
        """Export the results chart to an image file."""
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                title="Export Chart",
                initialdir=self.output_dir,
                filetypes=(("PNG files", "*.png"), ("All files", "*.*")),
                defaultextension=".png"
            )
        
        if file_path:
            # Make sure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Export Complete", f"Chart exported to {file_path}")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = ListeningTestApp(root)
    root.mainloop()