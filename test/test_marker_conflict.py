#!/usr/bin/env python3
"""
Test for marker code conflicts with actual data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor

def test_marker_conflict():
    """Test for marker code conflicts."""
    compressor = CircularChromosomeCompressor()
    
    # Create test data
    binary_data = bytearray()
    for i in range(1000):
        binary_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])
    
    original_bytes = bytes(binary_data)
    
    # Step through compression to get circular data
    dna_seq = compressor.binary_to_dna(original_bytes)
    compressed, dvnp_dict = compressor.dvnp_compress(str(dna_seq))
    circular_data = compressor.circular_encapsulate(compressed)
    
    print(f"Circular data length: {len(circular_data)}")
    print(f"Circular data range: {min(circular_data)} to {max(circular_data)}")
    print(f"Unique values in circular data: {len(set(circular_data))}")
    
    # Generate marker
    final_data, ts_metadata = compressor.add_trans_splicing_markers(circular_data, len(compressed))
    marker_code = ts_metadata['sl_marker_code']
    
    print(f"Marker code: {marker_code}")
    print(f"Marker code in circular data: {marker_code in circular_data}")
    
    if marker_code in circular_data:
        print(f"❌ CONFLICT! Marker code {marker_code} appears in actual data!")
        count_in_data = circular_data.count(marker_code)
        print(f"Marker code appears {count_in_data} times in circular data")
        
        # This will cause data loss during decompression
        filtered_data = [x for x in final_data if x != marker_code]
        expected_after_filter = len(circular_data)  # Should match original circular data
        actual_after_filter = len(filtered_data)
        
        print(f"Expected after filter: {expected_after_filter}")
        print(f"Actual after filter: {actual_after_filter}")
        print(f"Data loss: {expected_after_filter - actual_after_filter}")
        
        return False
    
    print(f"✓ No conflict! Marker code {marker_code} does not appear in data")
    return True

if __name__ == "__main__":
    success = test_marker_conflict()
    print(f"\n{'SUCCESS' if success else 'FAILURE'}")
