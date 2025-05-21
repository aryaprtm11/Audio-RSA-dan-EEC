import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import os
import sys
from typing import Tuple, Dict, Union, List
from datetime import datetime

# Add parent directory to sys.path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AudioSNREvaluator:
    def __init__(self):
        self.results = {}
        # Create output directory
        self.output_dir = "evaluations/output/snr"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file and return signal and sample rate."""
        try:
            signal, sample_rate = librosa.load(file_path, sr=None, mono=True)
            return signal, sample_rate
        except Exception as e:
            print(f"Error loading audio file {file_path}: {e}")
            return np.array([]), 0
            
    def calculate_snr(self, original: np.ndarray, modified: np.ndarray) -> float:
        """
        Calculate Signal-to-Noise Ratio.
        SNR = 10 * log10(signal_power / noise_power)
        """
        # Ensure signals have the same length
        min_length = min(len(original), len(modified))
        original = original[:min_length]
        modified = modified[:min_length]
        
        # Calculate noise as the difference between signals
        noise = original - modified
        
        # Calculate power
        signal_power = np.sum(original**2)
        noise_power = np.sum(noise**2)
        
        # Avoid division by zero
        if noise_power == 0:
            return float('inf')  # Perfect signal, no noise
            
        # Calculate SNR in dB
        snr = 10 * np.log10(signal_power / noise_power)
        return snr
    
    def evaluate(self, original_file: str, stego_file: str) -> Dict:
        """
        Evaluate steganography quality by comparing original and stego audio.
        """
        # Load audio files
        original, sr_original = self.load_audio(original_file)
        stego, sr_stego = self.load_audio(stego_file)
        
        if len(original) == 0 or len(stego) == 0:
            print("Error: Failed to load audio files.")
            return {}
            
        if sr_original != sr_stego:
            print(f"Warning: Sample rates differ - original: {sr_original}Hz, stego: {sr_stego}Hz")
            # Resample if needed
            if len(stego) > 0 and sr_stego > 0:
                stego = librosa.resample(stego, orig_sr=sr_stego, target_sr=sr_original)
        
        # Calculate SNR
        snr = self.calculate_snr(original, stego)
            
        # Store results
        result = {
            'original_file': original_file,
            'stego_file': stego_file,
            'snr': snr,
            'sample_rate': sr_original,
            'original_signal': original,
            'stego_signal': stego
        }
        
        key = f"{os.path.basename(original_file)}_vs_{os.path.basename(stego_file)}"
        self.results[key] = result
        
        return result
    
    def visualize_waveform_comparison(self, original_file: str, stego_file: str, output_file: str = None):
        """
        Visualize the waveform comparison between original and stego audio.
        """
        # Load and evaluate if not already done
        if not self.results:
            self.evaluate(original_file, stego_file)
        
        key = f"{os.path.basename(original_file)}_vs_{os.path.basename(stego_file)}"
        result = self.results[key]
        
        original_signal = result['original_signal']
        stego_signal = result['stego_signal']
        sample_rate = result['sample_rate']
        
        # Calculate time axis
        time = np.arange(0, len(original_signal)) / sample_rate
        
        # Create figure with subplots
        plt.figure(figsize=(14, 10))
        
        # Plot 1: Original audio waveform
        plt.subplot(3, 1, 1)
        plt.plot(time, original_signal, color='blue', alpha=0.8)
        plt.title(f'Original Audio Waveform: {os.path.basename(original_file)}')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Stego audio waveform
        plt.subplot(3, 1, 2)
        plt.plot(time, stego_signal, color='red', alpha=0.8)
        plt.title(f'Stego Audio Waveform: {os.path.basename(stego_file)}')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Difference (noise introduced by steganography)
        plt.subplot(3, 1, 3)
        plt.plot(time, stego_signal - original_signal, color='green')
        plt.title('Difference (Steganographic Noise)')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        
        # Add SNR information
        plt.figtext(0.5, 0.01, 
                   f"SNR: {result['snr']:.2f} dB - " + 
                   ("Excellent" if result['snr'] > 30 else 
                    "Good" if result['snr'] > 20 else 
                    "Acceptable" if result['snr'] > 10 else "Poor"),
                   ha="center", fontsize=12, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Set default output file if none provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/waveform_comparison_{key}_{timestamp}.png"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        plt.savefig(output_file)
        print(f"Waveform comparison saved to: {output_file}")
        
        plt.show()

# Direct comparison of two specific files
if __name__ == "__main__":
    evaluator = AudioSNREvaluator()
    
    print("===== AUDIO STEGANOGRAPHY WAVEFORM COMPARISON =====")
    
    # Define the paths to the original and stego files
    original_file = "../input/test_crypto.wav"
    stego_file = "../output/stego_test_crypto.wav"
    
    print(f"Original file: {original_file}")
    print(f"Stego file: {stego_file}")
    
    # Check if files exist
    if not os.path.exists(original_file):
        print(f"Error: Original file {original_file} does not exist.")
        sys.exit(1)
        
    if not os.path.exists(stego_file):
        print(f"Error: Stego file {stego_file} does not exist.")
        sys.exit(1)
    
    # Evaluate and visualize
    result = evaluator.evaluate(original_file, stego_file)
    
    if result:
        print(f"SNR: {result['snr']:.2f} dB")
        evaluator.visualize_waveform_comparison(original_file, stego_file)
        print("\nComparison complete. Check the output directory for results.")
    else:
        print("Error during evaluation. Could not compare the files.")