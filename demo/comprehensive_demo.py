#!/usr/bin/env python3
"""
Comprehensive CCC Feature Demonstration
Shows all major features of the Circular Chromosome Compression algorithm including:
- Layered architecture
- Enhanced error handling
- Shannon entropy analysis
- Complete compression pipeline
"""

import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.circular_chromosome_compression import CircularChromosomeCompressor

def demonstrate_layered_architecture():
    """Demonstrate the layered compression architecture."""
    print("=== Layered Architecture Demonstration ===")
    compressor = CircularChromosomeCompressor()
    
    test_data = b"This is a test of the layered architecture with repeated patterns and unique content."
    print(f"Original data: {test_data.decode()}")
    print(f"Original size: {len(test_data)} bytes\n")
    
    # Step 1: Core compression only
    print("Step 1: Core Compression Layer")
    core_compressed, core_metadata = compressor.compress_core(test_data)
    print(f"  Core compressed size: {len(core_compressed)} codes")
    print(f"  Core metadata: {core_metadata}")
    
    # Step 2: Encapsulation layer
    print("\nStep 2: Encapsulation Layer")
    encapsulated, encap_metadata = compressor.encapsulate(core_compressed)
    print(f"  Encapsulated size: {len(encapsulated)} codes")
    print(f"  Encapsulation metadata: {encap_metadata}")
    
    # Step 3: Complete pipeline
    print("\nStep 3: Complete Pipeline")
    full_compressed, full_metadata = compressor.compress(test_data)
    print(f"  Final compressed size: {len(full_compressed)} codes")
    print(f"  Complete metadata keys: {list(full_metadata.keys())}")
    
    # Verify consistency
    print(f"\nConsistency check: Encapsulated equals full? {encapsulated == full_compressed}")
    print()

def demonstrate_error_handling():
    """Demonstrate enhanced error handling modes."""
    print("=== Enhanced Error Handling Demonstration ===")
    
    # Test with invalid data
    invalid_data = b"Test data with some \x00\x01\x02 binary content"
    print(f"Testing with test data: {invalid_data}")
    
    # Strict mode (should fail gracefully for invalid inputs)
    print("\nStrict mode compressor:")
    strict_compressor = CircularChromosomeCompressor(strict_mode=True, verbose=True)
    try:
        result = strict_compressor.compress(invalid_data)
        print(f"  Compression successful: {len(result[0])} codes")
        print(f"  Metadata keys: {list(result[1].keys())}")
    except Exception as e:
        print(f"  Exception caught: {e}")
    
    # Lenient mode (should handle gracefully)
    print("\nLenient mode compressor:")
    lenient_compressor = CircularChromosomeCompressor(strict_mode=False, verbose=True)
    try:
        result = lenient_compressor.compress(invalid_data)
        print(f"  Compression successful: {len(result[0])} codes")
        print(f"  Metadata keys: {list(result[1].keys())}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    # Test with empty data to show validation
    print("\nEmpty data handling:")
    try:
        empty_result = strict_compressor.compress(b"")
        print(f"  Empty data result: {len(empty_result[0])} codes")
    except Exception as e:
        print(f"  Empty data exception: {e}")
    
    print()

def demonstrate_shannon_entropy():
    """Demonstrate Shannon entropy analysis."""
    print("=== Shannon Entropy Analysis Demonstration ===")
    compressor = CircularChromosomeCompressor()
    
    # Test different types of data
    test_cases = [
        ("Repetitive Pattern", b"ABCD" * 16),
        ("Text Data", b"The quick brown fox jumps over the lazy dog. " * 2),
        ("Binary Data", bytes(range(64))),
        ("Low Entropy", b"A" * 64),
    ]
    
    for name, data in test_cases:
        print(f"{name}:")
        print(f"  Data size: {len(data)} bytes")
        
        # Compress and analyze
        compressed = compressor.compress(data)
        stats = compressor.get_compression_stats(data, compressed)
        
        print(f"  Original entropy: {stats['original_entropy']:.3f} bits/byte")
        print(f"  Compressed entropy: {stats['compressed_entropy']:.3f} bits/byte")
        print(f"  Entropy reduction: {stats['entropy_reduction']:.3f} bits/byte")
        print(f"  Compression ratio: {stats['compression_ratio']:.3f}")
        print(f"  Theoretical minimum: {stats['theoretical_minimum_size']:.1f} bytes")
        print(f"  Shannon efficiency: {stats['shannon_efficiency']:.3f}")
        print(f"  Compression effectiveness: {stats['compression_effectiveness']:.3f}")
        print(f"  Space savings: {stats['space_savings_percent']:.1f}%")
        print()

def demonstrate_complete_pipeline():
    """Demonstrate the complete compression and decompression pipeline."""
    print("=== Complete Pipeline Demonstration ===")
    compressor = CircularChromosomeCompressor()
    
    # Test with a more substantial piece of data
    original_data = b"""
    The Circular Chromosome Compression (CCC) algorithm is a bio-inspired data compression method
    that mimics the structure and behavior of circular chromosomes found in bacteria and archaea.
    
    Key features include:
    - DVNP (Dynamic Variable-length Nucleotide Packing) compression
    - Circular encapsulation for enhanced redundancy
    - Trans-splicing markers for data integrity
    - Layered architecture for modularity
    - Enhanced error handling with strict/lenient modes
    - Shannon entropy analysis for theoretical evaluation
    
    This algorithm achieves compression ratios suitable for DNA storage applications while
    maintaining biological compatibility and providing comprehensive statistical analysis.
    """
    
    print(f"Original text length: {len(original_data)} bytes")
    print(f"First 100 characters: {original_data[:100].decode()}...")
    
    # Compress
    print("\nCompression phase:")
    compressed_result, metadata = compressor.compress(original_data)
    stats = compressor.get_compression_stats(original_data, (compressed_result, metadata))
    
    print(f"  Compressed to: {len(compressed_result)} codes")
    print(f"  Compression ratio: {stats['compression_ratio']:.3f}")
    print(f"  Space savings: {stats['space_savings_percent']:.1f}%")
    print(f"  Bits per base: {stats['bits_per_base']:.2f}")
    
    # Decompress
    print("\nDecompression phase:")
    decompressed_data = compressor.decompress(compressed_result, metadata)
    
    print(f"  Decompressed length: {len(decompressed_data)} bytes")
    print(f"  Data integrity: {'✓ PASSED' if decompressed_data == original_data else '✗ FAILED'}")
    
    # Entropy analysis
    print(f"\nEntropy analysis:")
    print(f"  Original entropy: {stats['original_entropy']:.3f} bits/byte")
    print(f"  Shannon efficiency: {stats['shannon_efficiency']:.3f}")
    print(f"  Compression effectiveness: {stats['compression_effectiveness']:.3f}")
    print()

def main():
    """Run all demonstrations."""
    print("🧬 Circular Chromosome Compression (CCC) - Comprehensive Feature Demo")
    print("=" * 70)
    print()
    
    demonstrate_layered_architecture()
    demonstrate_error_handling()
    demonstrate_shannon_entropy()
    demonstrate_complete_pipeline()
    
    print("=" * 70)
    print("🎉 All demonstrations completed successfully!")
    print("\nThe CCC algorithm now features:")
    print("✓ Layered architecture (core + encapsulation)")
    print("✓ Enhanced error handling (strict/lenient modes)")
    print("✓ Shannon entropy analysis")
    print("✓ Complete compression statistics")
    print("✓ Robust decompression with integrity verification")

if __name__ == '__main__':
    main()
