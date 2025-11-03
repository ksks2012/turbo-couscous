#!/usr/bin/env python3
"""
Test circular encapsulation and trans-splicing to isolate the issue.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor

def test_circular_and_markers():
    """Test circular encapsulation and trans-splicing markers."""
    compressor = CircularChromosomeCompressor()
    
    # Create test data similar to the failing case
    binary_data = bytearray()
    for i in range(100):  # Smaller test case
        binary_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])
    
    original_bytes = bytes(binary_data)
    
    print(f"Original data: {len(original_bytes)} bytes")
    
    # Step 1: Binary to DNA
    dna_seq = compressor.binary_to_dna(original_bytes)
    print(f"DNA length: {len(dna_seq)}")
    
    # Step 2: DVNP compression
    compressed, dvnp_dict = compressor.dvnp_compress(str(dna_seq))
    print(f"DVNP compressed: {len(compressed)} codes")
    
    # Step 3: Circular encapsulation
    circular_data = compressor.circular_encapsulate(compressed)
    print(f"Circular data: {len(circular_data)} codes")
    print(f"Original compressed length: {len(compressed)}")
    
    # Test: Can we recover the original compressed data?
    # The circular data should contain the original compressed data plus padding and bridge
    recovered_compressed = circular_data[:len(compressed)]
    print(f"Can recover original from circular: {recovered_compressed == compressed}")
    
    # Step 4: Add trans-splicing markers
    final_data, ts_metadata = compressor.add_trans_splicing_markers(circular_data, len(compressed))
    print(f"Final data with markers: {len(final_data)} codes")
    print(f"Trans-splicing metadata: {ts_metadata}")
    
    # Step 5: Test the reverse process
    
    # Remove markers
    marker_code = ts_metadata.get('sl_marker_code', 0)
    filtered_data = [x for x in final_data if x != marker_code]
    print(f"After removing markers: {len(filtered_data)} codes")
    
    # Remove circular encapsulation
    original_length = ts_metadata.get('original_length', len(filtered_data))
    original_compressed_length = ts_metadata.get('original_compressed_length', original_length)
    
    print(f"Original length: {original_length}")
    print(f"Original compressed length: {original_compressed_length}")
    
    if original_length <= len(filtered_data):
        encapsulated_data = filtered_data[:original_length]
        if original_compressed_length <= len(encapsulated_data):
            recovered_compressed_2 = encapsulated_data[:original_compressed_length]
        else:
            recovered_compressed_2 = filtered_data[:original_compressed_length]
    else:
        recovered_compressed_2 = filtered_data[:original_compressed_length]
    
    print(f"Recovered compressed length: {len(recovered_compressed_2)}")
    print(f"Matches original compressed: {recovered_compressed_2 == compressed}")
    
    if recovered_compressed_2 != compressed:
        print("❌ Cannot recover original compressed data!")
        print(f"Expected length: {len(compressed)}")
        print(f"Got length: {len(recovered_compressed_2)}")
        
        # Find first difference
        min_len = min(len(compressed), len(recovered_compressed_2))
        for i in range(min_len):
            if compressed[i] != recovered_compressed_2[i]:
                print(f"First difference at index {i}: expected {compressed[i]}, got {recovered_compressed_2[i]}")
                break
        
        return False
    
    # Step 6: DVNP decompress
    decompressed_dna = compressor.dvnp_decompress(recovered_compressed_2, dvnp_dict)
    print(f"DVNP decompressed DNA length: {len(decompressed_dna)}")
    print(f"DNA matches: {str(dna_seq) == decompressed_dna}")
    
    if str(dna_seq) != decompressed_dna:
        print("❌ DVNP decompression failed!")
        return False
    
    # Step 7: DNA to binary
    final_binary = compressor.dna_to_binary(decompressed_dna)
    print(f"Final binary length: {len(final_binary)}")
    
    # Ensure exact original length
    if len(final_binary) > len(original_bytes):
        final_binary = final_binary[:len(original_bytes)]
    elif len(final_binary) < len(original_bytes):
        padding_needed = len(original_bytes) - len(final_binary)
        final_binary = final_binary + b'\x00' * padding_needed
    
    print(f"After length adjustment: {len(final_binary)}")
    print(f"Final matches original: {final_binary == original_bytes}")
    
    if final_binary != original_bytes:
        print("❌ Final binary doesn't match!")
        # Find first difference
        for i, (orig, final) in enumerate(zip(original_bytes, final_binary)):
            if orig != final:
                print(f"First difference at byte {i}: expected {orig}, got {final}")
                break
        return False
    
    print("✓ All steps successful!")
    return True

if __name__ == "__main__":
    success = test_circular_and_markers()
    print(f"\n{'SUCCESS' if success else 'FAILURE'}")
