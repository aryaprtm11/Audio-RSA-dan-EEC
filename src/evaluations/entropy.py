import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from typing import Dict, List, Union, Tuple, Callable
import os
import sys
import json
import base64
import random
from datetime import datetime

# Add the parent directory to sys.path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import encryption modules
from crypto.ecc import SimplifiedECCCrypto
from crypto.rsa import SimpleRSACrypto
from core import prepare_message
from utils.bit_utils import text_to_bits, bits_to_text

class EntropyAnalyzer:
    def __init__(self):
        self.results = {}
        # Create output directory
        self.output_dir = "src/evaluations/output/entropy"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def calculate_shannon_entropy(self, data: Union[str, bytes, List[int]]) -> float:
        """
        Calculate the Shannon entropy of input data.
        H(X) = -sum(p(x) * log2(p(x))) for all x in X
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Count occurrences of each byte/symbol
        counter = Counter(data)
        length = len(data)
        
        # Calculate entropy
        entropy = 0
        for count in counter.values():
            probability = count / length
            entropy -= probability * np.log2(probability)
            
        return entropy
    
    def _generate_lorem_ipsum(self, length):
        """Generate random Lorem Ipsum text of specified length."""
        # Basic lorem ipsum words to choose from
        words = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", 
            "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "ut", 
            "enim", "ad", "minim", "veniam", "quis", "nostrud", "exercitation", "ullamco", "laboris", 
            "nisi", "ut", "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure", 
            "dolor", "in", "reprehenderit", "in", "voluptate", "velit", "esse", "cillum", "dolore", 
            "eu", "fugiat", "nulla", "pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non", 
            "proident", "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", 
            "est", "laborum"
        ]
        
        # Generate text by randomly choosing words until we reach or exceed the desired length
        result = ""
        while len(result) < length:
            word = random.choice(words)
            if len(result) + len(word) + 1 > length:
                if len(result) > 0:  # Only break if we have some text
                    break
                else:
                    # If result is still empty, just truncate the word
                    result = word[:length]
                    break
            result += " " + word if result else word
        
        # If we need to trim, do so
        return result[:length]
    
    def analyze_file(self, file_path: str, block_size: int = 1024) -> Dict:
        """Analyze entropy of a file in blocks."""
        result = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'block_entropy': [],
            'average_entropy': 0
        }
        
        total_entropy = 0
        block_count = 0
        
        with open(file_path, 'rb') as file:
            while True:
                block = file.read(block_size)
                if not block:
                    break
                
                entropy = self.calculate_shannon_entropy(block)
                result['block_entropy'].append(entropy)
                total_entropy += entropy
                block_count += 1
        
        if block_count > 0:
            result['average_entropy'] = total_entropy / block_count
        
        self.results[file_path] = result
        return result
    
    def compare_files(self, files: List[str], block_size: int = 1024) -> None:
        """Compare entropy of multiple files."""
        for file_path in files:
            self.analyze_file(file_path, block_size)
    
    def compare_data(self, data_dict: Dict[str, Union[str, bytes, List[int]]]) -> Dict:
        """Compare entropy of multiple data samples."""
        results = {}
        for name, data in data_dict.items():
            entropy = self.calculate_shannon_entropy(data)
            results[name] = {'entropy': entropy, 'length': len(data)}
            self.results[name] = results[name]
        return results
    
    def evaluate_encryption_entropy(self, plaintext_lengths=[5, 10, 15, 20, 25, 50, 100]):
        """
        Evaluates entropy when using the combined ECC+RSA encryption.
        
        Args:
            plaintext_lengths: List of plaintext lengths to test
        
        Returns:
            Dictionary with evaluation results
        """
        results = {
            "plaintext": {"lengths": [], "entropy": []},
            "ciphertext": {"lengths": [], "entropy": []},
            "percentage_improvement": []
        }
        
        # Generate sample text data of different lengths
        for length in plaintext_lengths:
            # Create random lorem ipsum text
            plaintext = self._generate_lorem_ipsum(length)
            
            print(f"\nTesting with plaintext length: {length}")
            print(f"Sample: {plaintext[:20]}{'...' if length > 20 else ''}")
            
            # Measure plaintext entropy
            pt_entropy = self.calculate_shannon_entropy(plaintext)
            
            try:
                # Encrypt using our actual encryption system (ECC+RSA combined)
                print("Encoding and encrypting with ECC+RSA combination...")
                all_bits, ecc_crypto, rsa_crypto = prepare_message(plaintext)
                
                # Convert bits back to bytes for entropy calculation
                ciphertext_bytes = bytes([int(all_bits[i:i+8], 2) for i in range(0, len(all_bits), 8)])
                
                # Measure ciphertext entropy
                ct_entropy = self.calculate_shannon_entropy(ciphertext_bytes)
                
                # Calculate percentage improvement
                if pt_entropy > 0:
                    improvement_percentage = ((ct_entropy - pt_entropy) / pt_entropy) * 100
                else:
                    improvement_percentage = 0  # Avoid division by zero
                
                # Store results
                results["plaintext"]["lengths"].append(length)
                results["plaintext"]["entropy"].append(pt_entropy)
                results["ciphertext"]["lengths"].append(len(ciphertext_bytes))
                results["ciphertext"]["entropy"].append(ct_entropy)
                results["percentage_improvement"].append(improvement_percentage)
                
                # Add to results dictionary for reporting
                self.results[f"Plaintext (length={length})"] = {
                    "entropy": pt_entropy,
                    "length": length
                }
                self.results[f"Ciphertext (from length={length})"] = {
                    "entropy": ct_entropy,
                    "length": len(ciphertext_bytes),
                    "improvement_percentage": improvement_percentage
                }
                
                print(f"Results - Plaintext entropy: {pt_entropy:.4f} bits, Ciphertext entropy: {ct_entropy:.4f} bits")
                print(f"Entropy improvement: {improvement_percentage:.2f}%")
                print(f"Original size: {length} bytes, Encrypted size: {len(ciphertext_bytes)} bytes")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error processing length {length}: {str(e)}")
                continue
        
        return results
    
    def visualize_encryption_evaluation(self, results, title="Entropy Analysis by Plaintext Length", output_file=None):
        """Visualize encryption entropy evaluation results."""
        plt.figure(figsize=(12, 7))
        
        # Create subplot 1: Traditional entropy comparison
        plt.subplot(1, 2, 1)
        plt.plot(results["plaintext"]["lengths"], results["plaintext"]["entropy"], 'b-o', label="Plaintext")
        plt.plot(results["plaintext"]["lengths"], results["ciphertext"]["entropy"], 'r-o', label="Ciphertext")
        plt.axhline(y=8.0, color='green', linestyle='--', label='Maximum entropy (8 bits)')
        
        plt.title("Raw Entropy Values")
        plt.xlabel("Plaintext Length")
        plt.ylabel("Entropy (bits)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Create subplot 2: Percentage improvement
        plt.subplot(1, 2, 2)
        bars = plt.bar(results["plaintext"]["lengths"], results["percentage_improvement"], color='purple')
        
        plt.title("Entropy Improvement Percentage")
        plt.xlabel("Plaintext Length")
        plt.ylabel("Improvement (%)")
        plt.grid(True, alpha=0.3)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Set default output file if none provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/entropy_evaluation_{timestamp}.png"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        plt.savefig(output_file)
        print(f"Encryption evaluation chart saved to: {output_file}")
        plt.show()
    
    def visualize_entropy(self, title: str = "Entropy Analysis", output_file: str = None) -> None:
        """Visualize entropy comparison."""
        plt.figure(figsize=(12, 8))
        
        # Bar chart for average entropy
        labels = []
        values = []
        
        for name, result in self.results.items():
            if isinstance(result, dict):
                if 'average_entropy' in result:
                    labels.append(os.path.basename(name))
                    values.append(result['average_entropy'])
                elif 'entropy' in result:
                    labels.append(name)
                    values.append(result['entropy'])
        
        plt.bar(labels, values, color='skyblue')
        plt.axhline(y=8.0, color='red', linestyle='--', label='Maximum entropy (8 bits)')
        
        plt.title(title)
        plt.xlabel("Data Source")
        plt.ylabel("Entropy (bits)")
        plt.ylim(0, 8.5)  # Shannon entropy for bytes maxes out at 8 bits
        plt.grid(axis='y', alpha=0.3)
        plt.legend()
        
        # Rotate x-axis labels if there are many
        if len(labels) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Set default output file if none provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/entropy_comparison_{timestamp}.png"
        
        # Ensure directory exists for the output file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        plt.savefig(output_file)
        print(f"Entropy comparison chart saved to: {output_file}")
        
        plt.show()
    
    def plot_entropy_distribution(self, file_or_name: str, output_file: str = None) -> None:
        """Plot entropy distribution for blocks of a file."""
        if file_or_name not in self.results:
            print(f"No analysis found for {file_or_name}")
            return
        
        result = self.results[file_or_name]
        if 'block_entropy' not in result or not result['block_entropy']:
            print(f"No block entropy data found for {file_or_name}")
            return
            
        plt.figure(figsize=(12, 6))
        
        block_numbers = range(1, len(result['block_entropy']) + 1)
        plt.plot(block_numbers, result['block_entropy'], marker='o', linestyle='-', markersize=3)
        
        plt.axhline(y=result['average_entropy'], color='red', linestyle='--', 
                   label=f"Avg: {result['average_entropy']:.4f} bits")
        
        plt.title(f"Entropy Distribution: {os.path.basename(file_or_name)}")
        plt.xlabel("Block Number")
        plt.ylabel("Entropy (bits)")
        plt.ylim(0, 8.5)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        # Set default output file if none provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            basename = os.path.basename(file_or_name) if isinstance(file_or_name, str) else "data"
            output_file = f"{self.output_dir}/entropy_distribution_{basename}_{timestamp}.png"
        
        # Ensure directory exists for the output file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        plt.savefig(output_file)
        print(f"Entropy distribution chart saved to: {output_file}")
        
        plt.show()
    
    def generate_report(self, output_file: str = None) -> None:
        """Generate a text report of entropy analysis results."""
        # Set default output file if none provided
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{self.output_dir}/entropy_analysis_report_{timestamp}.txt"
        
        # Ensure directory exists for the output file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("===== Entropy Analysis Report =====\n\n")
            
            for name, result in self.results.items():
                f.write(f"Source: {name}\n")
                
                if 'average_entropy' in result:
                    f.write(f"File Size: {result['file_size']} bytes\n")
                    f.write(f"Average Entropy: {result['average_entropy']:.6f} bits\n")
                    f.write(f"Block Count: {len(result['block_entropy'])}\n")
                    f.write(f"Min Block Entropy: {min(result['block_entropy']):.6f} bits\n")
                    f.write(f"Max Block Entropy: {max(result['block_entropy']):.6f} bits\n")
                elif 'entropy' in result:
                    f.write(f"Data Length: {result['length']} bytes/symbols\n")
                    f.write(f"Entropy: {result['entropy']:.6f} bits\n")
                    if 'improvement_percentage' in result:
                        f.write(f"Improvement Percentage: {result['improvement_percentage']:.2f}%\n")
                
                # Add entropy quality assessment
                entropy_value = result.get('average_entropy', result.get('entropy', 0))
                quality = self._assess_entropy_quality(entropy_value)
                f.write(f"Entropy Quality: {quality}\n")
                
                f.write("\n" + "-"*40 + "\n\n")
            
            f.write("\nHigher entropy (closer to 8 bits) generally indicates more randomness,\n")
            f.write("which is desirable for encrypted data. Plain text typically has lower entropy.\n")
        
        print(f"Report generated: {output_file}")
    
    def _assess_entropy_quality(self, entropy):
        """Assess the quality of entropy value."""
        if entropy >= 7.5:
            return "Excellent (Very Random)"
        elif entropy >= 6.5:
            return "Good (Sufficient Randomness)"
        elif entropy >= 5.0:
            return "Moderate (Some Patterns Present)"
        elif entropy >= 3.0:
            return "Low (Many Patterns)"
        else:
            return "Poor (Highly Predictable)"

# Example usage
if __name__ == "__main__":
    analyzer = EntropyAnalyzer()
    
    print("===== ENTROPY ANALYSIS OF ENCRYPTION =====")
    
    # Evaluate combined ECC+RSA encryption on different plaintext lengths
    print("\nEVALUATING ENCRYPTION ACROSS DIFFERENT PLAINTEXT LENGTHS")
    results = analyzer.evaluate_encryption_entropy(
        plaintext_lengths=[10, 20, 50, 100, 200, 500]
    )
    analyzer.visualize_encryption_evaluation(results, "ECC+RSA Encryption Entropy Analysis")
    
    # Generate comprehensive report
    analyzer.generate_report()
    
    print("\nAll evaluations complete. Check the output directory for results.")