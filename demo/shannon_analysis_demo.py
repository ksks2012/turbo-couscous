#!/usr/bin/env python3
"""
CCC Shannon Entropy Analysis Demo
Demonstrates theoretical analysis and practical performance of compression efficiency
"""

import sys
import os
import time

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.circular_chromosome_compression import CircularChromosomeCompressor


def demonstrate_shannon_analysis():
    """Demonstrate Shannon entropy analysis functionality"""
    
    print("=" * 80)
    print("CCC Shannon Entropy Analysis & Compression Efficiency Assessment")
    print("=" * 80)
    
    compressor = CircularChromosomeCompressor(verbose=False)
    
    # Prepare test data with different entropy values
    test_datasets = [
        # Minimum entropy: single value
        (b'\x00' * 1000, "Zero-filled data", "Minimum entropy (0 bits/byte)"),
        
        # Low entropy: few repeated values
        (b'AAAAAABBBBBB' * 83, "Binary repeated data", "Low entropy (1 bits/byte)"),
        
        # Medium entropy: text data
        (b'The quick brown fox jumps over the lazy dog. ' * 22, "English text", "Medium entropy (~4 bits/byte)"),
        
        # High entropy: random data
        (os.urandom(1000), "Random data", "High entropy (near 8 bits/byte)"),
        
        # Special pattern: structured data
        (bytes(range(256)) * 4, "Sequential data", "Uniform distribution (8 bits/byte)"),
        
        # DNA related: four nucleotides
        (b'ACGTACGTACGT' * 83, "DNA sequence simulation", "DNA pattern (2 bits/byte)")
    ]
    
    print("\n📊 Shannon Entropy Analysis Report:")
    print("=" * 80)
    
    results = []
    
    for data, name, description in test_datasets:
        print(f"\n🧬 {name} ({description})")
        print("-" * 60)
        
        # Execute compression
        start_time = time.time()
        compressed, metadata = compressor.compress(data)
        compress_time = time.time() - start_time
        
        # Get detailed statistics
        stats = compressor.get_compression_stats(data, compressed)
        
        # Basic information
        print(f"   Data size:              {len(data):,} bytes")
        print(f"   Compression time:       {compress_time * 1000:.1f} ms")
        
        # Shannon entropy analysis
        print(f"   Shannon entropy:        {stats['original_entropy']:.3f} bits/byte")
        print(f"   Theoretical min size:   {stats['theoretical_minimum_size']:.0f} bytes")
        print(f"   Actual compressed size: {stats['compressed_size_bytes']:,} bytes")
        
        # Efficiency metrics
        print(f"   Compression ratio:      {stats['compression_ratio']:.3f}")
        print(f"   Space savings:          {stats['space_savings_percent']:.1f}%")
        print(f"   Shannon efficiency:     {stats['shannon_efficiency']:.3f}")
        print(f"   Compression effectiveness: {stats['compression_effectiveness']:.3f}")
        
        # DNA storage related
        print(f"   DNA bits/base:          {stats['bits_per_base']:.3f}")
        
        # Performance evaluation
        efficiency = stats['shannon_efficiency']
        if efficiency > 0.7:
            rating = "🟢 Excellent"
        elif efficiency > 0.4:
            rating = "🟡 Good"
        elif efficiency > 0.1:
            rating = "🟠 Fair"
        else:
            rating = "🔴 Needs improvement"
        
        print(f"   Compression performance: {rating}")
        
        results.append((name, stats))
    
    # Summary analysis
    print("\n" + "=" * 80)
    print("📈 Compression Efficiency Summary Analysis")
    print("=" * 80)
    
    print("\n🔍 Shannon Entropy Theory Explanation:")
    print("   • 0 bits/byte:     Completely repetitive data (e.g., all zeros)")
    print("   • 1-2 bits/byte:   Low entropy data (high repetitiveness)")  
    print("   • 3-5 bits/byte:   Medium entropy data (text, structured)")
    print("   • 6-8 bits/byte:   High entropy data (random, encrypted)")
    
    print("\n📊 Efficiency Metrics Interpretation:")
    print("   • Shannon efficiency:    Degree to which actual compression approaches theoretical limit")
    print("   • Compression effectiveness: Compression improvement relative to theoretical entropy")
    print("   • DNA bits/base:         Information density for DNA storage")
    
    print("\n🎯 CCC Algorithm Characteristics:")
    print("   • Optimized for DNA storage, includes biological compatibility overhead")
    print("   • Performs best on low entropy data (repetitive patterns)")
    print("   • High entropy data may expand due to DNA conversion overhead")
    print("   • Suitable for long-term storage and biological system integration")
    
    # Best and worst cases
    best_efficiency = max(results, key=lambda x: x[1]['shannon_efficiency'])
    worst_efficiency = min(results, key=lambda x: x[1]['shannon_efficiency'])
    
    print(f"\n🏆 Best compression efficiency: {best_efficiency[0]} ({best_efficiency[1]['shannon_efficiency']:.3f})")
    print(f"⚠️  Worst compression efficiency: {worst_efficiency[0]} ({worst_efficiency[1]['shannon_efficiency']:.3f})")


def demonstrate_compression_comparison():
    """Compare compression performance across different data types"""
    
    print("\n" + "=" * 80)
    print("🔬 Compression Performance Comparison Analysis")
    print("=" * 80)
    
    compressor = CircularChromosomeCompressor()
    
    # Generate test data with different entropy values
    test_patterns = [
        ("Repetitive", b'A' * 1000),
        ("Binary", b'\x00\x01' * 500), 
        ("Quaternary", b'\x00\x01\x02\x03' * 250),
        ("Text", b'Hello World! ' * 77),
        ("Random", os.urandom(1000))
    ]
    
    print(f"{'Data Type':<12} {'Entropy':<8} {'Ratio':<8} {'Shannon Eff':<12} {'Grade':<8}")
    print("-" * 60)
    
    for pattern_name, data in test_patterns:
        compressed, _ = compressor.compress(data)
        stats = compressor.get_compression_stats(data, compressed)
        
        # Assessment grade
        eff = stats['shannon_efficiency']
        if eff > 0.5:
            grade = "Excellent"
        elif eff > 0.2:
            grade = "Good"
        else:
            grade = "Fair"
        
        print(f"{pattern_name:<12} {stats['original_entropy']:<8.3f} {stats['compression_ratio']:<8.3f} {stats['shannon_efficiency']:<12.3f} {grade:<8}")


if __name__ == "__main__":
    demonstrate_shannon_analysis()
    demonstrate_compression_comparison()
