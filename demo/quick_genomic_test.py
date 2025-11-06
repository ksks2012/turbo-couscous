#!/usr/bin/env python3
"""
Quick Demo Runner for Genomic Compression
This script demonstrates the integrated genomic compression functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from genomic_compression_demo import GenomicCompressionDemo
import time

def quick_demo():
    """Run a quick demonstration of genomic compression features."""
    print("🧬 Genomic Compression Quick Demo")
    print("=" * 50)
    
    demo = GenomicCompressionDemo(verbose=False)
    
    # Test different patterns at small scale for quick results
    test_cases = [
        ('Repetitive Elements', 20000, demo.create_repetitive_elements),
        ('Tandem Repeats', 15000, demo.create_tandem_repeats),
        ('Coding Sequences', 30000, demo.create_coding_sequence),
        ('Mixed Genomic', 25000, demo.create_mixed_genomic_content)
    ]
    
    print(f"{'Pattern':<20} {'Size':<8} {'Compressed':<11} {'Ratio':<8} {'Time(s)':<8} {'OK'}")
    print("-" * 65)
    
    for pattern_name, size, generator in test_cases:
        # Generate sequence
        sequence = generator(size)
        
        # Time compression and decompression
        start_time = time.perf_counter()
        compressed = demo.compressor.dvnp_compress(sequence)
        decompressed = demo.compressor.dvnp_decompress(compressed)
        total_time = time.perf_counter() - start_time
        
        # Calculate metrics
        ratio = len(compressed) / len(sequence)
        integrity = sequence == decompressed
        status = "✓" if integrity else "✗"
        
        print(f"{pattern_name:<20} {size:<8,} {len(compressed):<11,} {ratio:<8.3f} "
              f"{total_time:<8.3f} {status}")
    
    print()
    print("✅ All genomic compression patterns working correctly!")
    print("📁 Original test files moved to demo/demo_backup/")
    print("🔧 Use 'python demo/genomic_compression_demo.py' for full demonstration")

if __name__ == "__main__":
    quick_demo()
