#!/usr/bin/env python3
"""
Test the LZW algorithm independently to isolate the issue.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor

def test_lzw_algorithm():
    """Test the LZW algorithm with known data."""
    compressor = CircularChromosomeCompressor()
    
    # Test with simple repetitive DNA sequence
    test_sequences = [
        "AAAA",
        "ACGTACGT",
        "AAACCCGGGTTT",
        "ACGTACGTACGTACGT",  # Longer repetitive sequence
        "ATCGATCGATCGATCG"   # Different pattern
    ]
    
    for seq in test_sequences:
        print(f"\nTesting: {seq}")
        
        # Compress
        compressed, dictionary = compressor.dvnp_compress(seq)
        print(f"Compressed: {compressed}")
        print(f"Dictionary: {dictionary}")
        
        # Decompress
        decompressed = compressor.dvnp_decompress(compressed, dictionary)
        print(f"Decompressed: {decompressed}")
        
        # Check
        matches = seq == decompressed
        print(f"Match: {matches}")
        
        if not matches:
            print(f"❌ MISMATCH!")
            print(f"Expected: {seq}")
            print(f"Got:      {decompressed}")
            return False
    
    print("\n✓ All simple tests passed!")
    
    # Now test with the problematic pattern
    print("\n=== Testing problematic pattern ===")
    
    # Create similar pattern to the failing test
    binary_data = bytearray()
    for i in range(100):  # Smaller version
        binary_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])
    
    dna_seq = compressor.binary_to_dna(bytes(binary_data))
    print(f"DNA sequence length: {len(dna_seq)}")
    
    compressed, dictionary = compressor.dvnp_compress(str(dna_seq))
    decompressed = compressor.dvnp_decompress(compressed, dictionary)
    
    matches = str(dna_seq) == decompressed
    print(f"LZW Match: {matches}")
    
    if not matches:
        print("❌ LZW fails on this pattern!")
        # Find where it differs
        for i, (orig, decomp) in enumerate(zip(str(dna_seq), decompressed)):
            if orig != decomp:
                print(f"First difference at position {i}: expected '{orig}', got '{decomp}'")
                print(f"Context: {str(dna_seq)[max(0,i-10):i+10]}")
                print(f"         {decompressed[max(0,i-10):i+10]}")
                break
        return False
    
    print("✓ LZW works on this pattern!")
    return True

if __name__ == "__main__":
    success = test_lzw_algorithm()
    print(f"\n{'SUCCESS' if success else 'FAILURE'}")
