#!/usr/bin/env python3
"""
Large file performance test for CCC algorithm.
Tests files up to 100MB to evaluate scalability and performance.
"""

import sys
import os
import time
import json
import gc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor
from utils import helpers

def create_large_test_data(size: int, pattern: str = 'mixed') -> bytes:
    """Create large test data with specified pattern."""
    if pattern == 'mixed':
        # Create mixed pattern data that's more realistic
        chunks = []
        chunk_patterns = [
            b'TEXT_DATA_CHUNK' * 100,  # Text-like data
            bytes(range(256)) * 4,     # Binary sequence
            b'\x00' * 1000,           # Zero blocks
            b'REPEAT' * 200,          # Repetitive patterns
        ]
        
        chunk_size = 4096  # 4KB chunks
        for i in range(0, size, chunk_size):
            pattern_idx = (i // chunk_size) % len(chunk_patterns)
            chunk = chunk_patterns[pattern_idx]
            remaining = min(chunk_size, size - i)
            chunks.append((chunk * (remaining // len(chunk) + 1))[:remaining])
        
        return b''.join(chunks)
    
    elif pattern == 'repetitive':
        base_pattern = b'ABCDEFGHIJKLMNOP' * 64  # 1KB base pattern
        return (base_pattern * (size // len(base_pattern) + 1))[:size]
    
    elif pattern == 'random':
        return bytes([(i * 17 + 23) % 256 for i in range(size)])
    
    elif pattern == 'text':
        text_block = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        text_bytes = text_block.encode('utf-8')
        return (text_bytes * (size // len(text_bytes) + 1))[:size]
    
    else:  # sequential
        return bytes([i % 256 for i in range(size)])

def run_large_file_tests():
    """Run large file performance tests."""
    compressor = CircularChromosomeCompressor(chunk_size=10000)  # Larger chunks for big files
    
    print("=== CCC Large File Performance Test ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test sizes from 1MB to 100MB
    test_sizes = [
        1048576,    # 1MB
        5242880,    # 5MB
        10485760,   # 10MB
        20971520,   # 20MB
        52428800,   # 50MB
        104857600,  # 100MB
    ]
    
    test_patterns = ['mixed', 'repetitive', 'text']
    
    results = []
    
    for size in test_sizes:
        size_mb = size // 1048576
        print(f"\n=== Testing {size_mb}MB files ===")
        
        for pattern in test_patterns:
            print(f"Pattern: {pattern}")
            
            try:
                # Generate test data
                print("  Generating test data...")
                test_data = create_large_test_data(size, pattern)
                
                # Force garbage collection before test
                gc.collect()
                
                # Compression test
                print("  Compressing...")
                start_time = time.time()
                compressed_data, metadata = compressor.compress(test_data)
                compression_time = time.time() - start_time
                
                # Calculate compression stats
                stats = compressor.get_compression_stats(test_data, compressed_data)
                
                print("  Decompressing...")
                start_time = time.time()
                decompressed_data = compressor.decompress(compressed_data, metadata)
                decompression_time = time.time() - start_time
                
                # Verify integrity
                integrity_ok = (test_data == decompressed_data)
                
                # Calculate throughput
                comp_throughput_mb_s = size / compression_time / 1048576
                decomp_throughput_mb_s = size / decompression_time / 1048576
                
                result = {
                    'size_mb': size_mb,
                    'pattern': pattern,
                    'compression_time_sec': compression_time,
                    'decompression_time_sec': decompression_time,
                    'compression_throughput_mb_s': comp_throughput_mb_s,
                    'decompression_throughput_mb_s': decomp_throughput_mb_s,
                    'compression_ratio': stats['compression_ratio'],
                    'compressed_size_mb': stats['compressed_size_bytes'] / 1048576,
                    'bits_per_base': stats['bits_per_base'],
                    'integrity_verified': integrity_ok
                }
                
                results.append(result)
                
                print(f"  ✓ Compression: {comp_throughput_mb_s:.2f} MB/s")
                print(f"  ✓ Decompression: {decomp_throughput_mb_s:.2f} MB/s") 
                print(f"  ✓ Ratio: {stats['compression_ratio']:.3f}")
                print(f"  ✓ Integrity: {'PASS' if integrity_ok else 'FAIL'}")
                
                # Clean up memory
                del test_data
                del compressed_data
                del decompressed_data
                gc.collect()
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                results.append({
                    'size_mb': size_mb,
                    'pattern': pattern,
                    'error': str(e)
                })
    
    # Generate summary report
    print(f"\n=== Performance Summary ===")
    print(f"{'Size':<8} {'Pattern':<12} {'Comp MB/s':<12} {'Decomp MB/s':<14} {'Ratio':<8} {'Status'}")
    print("-" * 80)
    
    successful_tests = [r for r in results if 'error' not in r and r['integrity_verified']]
    
    for result in successful_tests:
        print(f"{result['size_mb']:>4}MB   {result['pattern']:<12} "
              f"{result['compression_throughput_mb_s']:>8.2f}     "
              f"{result['decompression_throughput_mb_s']:>10.2f}      "
              f"{result['compression_ratio']:>5.3f}   ✓")
    
    if successful_tests:
        # Calculate averages
        avg_comp_speed = sum(r['compression_throughput_mb_s'] for r in successful_tests) / len(successful_tests)
        avg_decomp_speed = sum(r['decompression_throughput_mb_s'] for r in successful_tests) / len(successful_tests)
        avg_ratio = sum(r['compression_ratio'] for r in successful_tests) / len(successful_tests)
        
        print(f"\nAverage Performance:")
        print(f"  Compression speed: {avg_comp_speed:.2f} MB/s")
        print(f"  Decompression speed: {avg_decomp_speed:.2f} MB/s")
        print(f"  Compression ratio: {avg_ratio:.3f}")
    
    # Save results
    test_summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_results': results,
        'successful_tests': len(successful_tests),
        'total_tests': len(results),
        'success_rate': len(successful_tests) / len(results) if results else 0
    }
    
    if successful_tests:
        test_summary['performance_summary'] = {
            'avg_compression_throughput_mb_s': avg_comp_speed,
            'avg_decompression_throughput_mb_s': avg_decomp_speed,
            'avg_compression_ratio': avg_ratio
        }
    
    with open('large_file_test_results.json', 'w') as f:
        json.dump(test_summary, f, indent=2)
    
    print(f"\nDetailed results saved to: large_file_test_results.json")
    print(f"Test success rate: {test_summary['success_rate']*100:.1f}%")
    
    return test_summary['success_rate'] == 1.0

if __name__ == "__main__":
    print("Warning: This test will consume significant memory and time.")
    print("Testing files up to 100MB in size.")
    
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    success = run_large_file_tests()
    sys.exit(0 if success else 1)
