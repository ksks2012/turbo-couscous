#!/usr/bin/env python3
"""
Test with the exact same data pattern as the failing test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor

def test_exact_failing_pattern():
    """Test with the exact pattern from the failing test."""
    compressor = CircularChromosomeCompressor()
    
    # Create exactly the same data as the failing test
    binary_data = bytearray()
    for i in range(1000):  # Exact same loop
        binary_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])
    
    original_bytes = bytes(binary_data)
    print(f"Original data: {len(original_bytes)} bytes")
    
    # Test step by step, similar to the manual decompression process
    
    # Full compression
    compressed_data, metadata = compressor.compress(original_bytes)
    print(f"Compressed data length: {len(compressed_data)}")
    print(f"Metadata: {metadata}")
    
    # Manual decompression process (following the exact same steps as decompress method)
    ts_metadata = metadata.get('trans_splicing', {})
    marker_code = ts_metadata.get('sl_marker_code', 0)
    
    print(f"\nMarker code: {marker_code}")
    
    # Filter out markers
    filtered_data = [x for x in compressed_data if x != marker_code]
    print(f"After removing markers: {len(filtered_data)} codes")
    
    # Remove bridge elements and zero padding from circular encapsulation
    original_length = ts_metadata.get('original_length', len(filtered_data))
    original_compressed_length = ts_metadata.get('original_compressed_length', original_length)
    
    print(f"Original length from metadata: {original_length}")
    print(f"Original compressed length from metadata: {original_compressed_length}")
    
    if original_length <= len(filtered_data):
        encapsulated_data = filtered_data[:original_length]
        print(f"Encapsulated data length: {len(encapsulated_data)}")
        
        # Extract only the original compressed data, excluding zero padding and bridge elements
        if original_compressed_length <= len(encapsulated_data):
            circular_data = encapsulated_data[:original_compressed_length]
        else:
            print(f"Warning: original_compressed_length ({original_compressed_length}) > encapsulated_data length ({len(encapsulated_data)})")
            circular_data = encapsulated_data
    else:
        print(f"Warning: original_length ({original_length}) > filtered_data length ({len(filtered_data)})")
        circular_data = filtered_data[:original_compressed_length] if original_compressed_length <= len(filtered_data) else filtered_data
    
    print(f"Circular data for DVNP: {len(circular_data)} codes")
    
    # DVNP decompression
    dvnp_dict = metadata.get('dvnp_dictionary', {})
    print(f"DVNP dictionary: {dvnp_dict}")
    
    try:
        dna_sequence = compressor.dvnp_decompress(circular_data, dvnp_dict)
        print(f"DVNP decompressed DNA length: {len(dna_sequence)}")
    except Exception as e:
        print(f"❌ DVNP decompression failed: {e}")
        return False
    
    # Convert DNA back to binary
    binary_data_recovered = compressor.dna_to_binary(dna_sequence)
    print(f"Recovered binary length: {len(binary_data_recovered)}")
    
    # Ensure exact original length
    expected_size = metadata.get('original_size', len(original_bytes))
    print(f"Expected size from metadata: {expected_size}")
    
    if len(binary_data_recovered) > expected_size:
        print(f"Truncating from {len(binary_data_recovered)} to {expected_size}")
        binary_data_recovered = binary_data_recovered[:expected_size]
    elif len(binary_data_recovered) < expected_size:
        padding_needed = expected_size - len(binary_data_recovered)
        print(f"Padding with {padding_needed} zero bytes")
        binary_data_recovered = binary_data_recovered + b'\x00' * padding_needed
    
    print(f"Final binary length: {len(binary_data_recovered)}")
    
    # Compare
    matches = original_bytes == binary_data_recovered
    print(f"Manual decompression matches: {matches}")
    
    if not matches:
        # Find first difference
        for i, (orig, recovered) in enumerate(zip(original_bytes, binary_data_recovered)):
            if orig != recovered:
                print(f"First difference at byte {i}: expected {orig}, got {recovered}")
                print(f"Original context: {original_bytes[max(0,i-5):i+5]}")
                print(f"Recovered context: {binary_data_recovered[max(0,i-5):i+5]}")
                break
    
    # Now test the automatic decompression
    auto_decompressed = compressor.decompress(compressed_data, metadata)
    auto_matches = original_bytes == auto_decompressed
    print(f"Auto decompression matches: {auto_matches}")
    
    return matches and auto_matches

if __name__ == "__main__":
    success = test_exact_failing_pattern()
    print(f"\n{'SUCCESS' if success else 'FAILURE'}")
