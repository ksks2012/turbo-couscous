#!/usr/bin/env python3
"""
Comprehensive performance and correctness test for CCC algorithm.
"""

import sys
import os
import time
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor
from utils import helpers
import tempfile

def create_test_data(size: int, pattern: str = 'random') -> bytes:
    """Create test data of specified size and pattern."""
    if pattern == 'random':
        return bytes([(i * 17) % 256 for i in range(size)])
    elif pattern == 'repetitive':
        base = b'ABCDEFGH' * 32  # 256 bytes
        return (base * (size // len(base) + 1))[:size]
    elif pattern == 'zeros':
        return b'\x00' * size
    elif pattern == 'text':
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        return (text.encode('utf-8') * (size // len(text.encode('utf-8')) + 1))[:size]
    else:
        return bytes(range(256)) * (size // 256) + bytes(range(size % 256))

def run_comprehensive_tests():
    """Run comprehensive correctness and performance tests."""
    compressor = CircularChromosomeCompressor()
    
    print("=== CCC Algorithm Comprehensive Test Suite ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Correctness tests with various data patterns
    print("1. Correctness Tests")
    print("-" * 50)
    
    test_sizes = [100, 500, 1024, 5000, 10000]
    test_patterns = ['random', 'repetitive', 'zeros', 'text', 'sequential']
    
    correctness_results = []
    
    for size in test_sizes:
        for pattern in test_patterns:
            test_data = create_test_data(size, pattern)
            
            # Compress and decompress
            compressed, metadata = compressor.compress(test_data)
            decompressed = compressor.decompress(compressed, metadata)
            
            # Verify integrity
            integrity_ok = (test_data == decompressed)
            
            # Calculate stats
            stats = compressor.get_compression_stats(test_data, compressed)
            
            result = {
                'size': size,
                'pattern': pattern,
                'integrity_ok': integrity_ok,
                'compression_ratio': stats['compression_ratio'],
                'bits_per_base': stats['bits_per_base']
            }
            correctness_results.append(result)
            
            status = "✓" if integrity_ok else "✗"
            print(f"{status} Size: {size:>5}B, Pattern: {pattern:<11}, Ratio: {stats['compression_ratio']:.3f}")
    
    # Test 2: Performance benchmarks
    print(f"\n2. Performance Benchmarks")
    print("-" * 50)
    
    perf_sizes = [1024, 4096, 16384, 65536, 262144, 1048576, 5242880, 10485760, 52428800, 104857600]  # 1KB to 100MB
    performance_results = []
    
    for size in perf_sizes:
        test_data = create_test_data(size, 'random')
        
        # Measure compression time
        start_time = time.time()
        compressed, metadata = compressor.compress(test_data)
        compression_time = time.time() - start_time
        
        # Measure decompression time
        start_time = time.time()
        decompressed = compressor.decompress(compressed, metadata)
        decompression_time = time.time() - start_time
        
        # Calculate throughput
        comp_throughput = size / compression_time if compression_time > 0 else 0
        decomp_throughput = size / decompression_time if decompression_time > 0 else 0
        
        # Verify integrity
        integrity_ok = (test_data == decompressed)
        
        # Calculate compression stats
        stats = compressor.get_compression_stats(test_data, compressed)
        
        result = {
            'size': size,
            'compression_time': compression_time,
            'decompression_time': decompression_time,
            'compression_throughput_kb_s': comp_throughput / 1024,
            'decompression_throughput_kb_s': decomp_throughput / 1024,
            'compression_ratio': stats['compression_ratio'],
            'integrity_ok': integrity_ok
        }
        performance_results.append(result)
        
        if size >= 1048576:
            size_str = f"{size//1048576}MB"
        elif size >= 1024:
            size_str = f"{size//1024}KB"
        else:
            size_str = f"{size}B"
        print(f"Size: {size_str:>6} | Comp: {comp_throughput/1024:>7.1f} KB/s | Decomp: {decomp_throughput/1024:>7.1f} KB/s | Ratio: {stats['compression_ratio']:.3f} | {('✓' if integrity_ok else '✗')}")
    
    # Test 3: Scalability tests
    print(f"\n3. Scalability Tests")
    print("-" * 50)
    
    scalability_results = []
    
    for size in [10240, 51200, 102400, 1048576, 10485760]:  # 10KB, 50KB, 100KB, 1MB, 10MB
        test_data = create_test_data(size, 'random')
        
        # Measure processing time
        start_time = time.time()
        compressed, metadata = compressor.compress(test_data)
        decompressed = compressor.decompress(compressed, metadata)
        total_time = time.time() - start_time
        
        # Calculate efficiency metrics
        throughput = size / total_time if total_time > 0 else 0
        integrity_ok = (test_data == decompressed)
        
        result = {
            'size': size,
            'total_time': total_time,
            'throughput_kb_s': throughput / 1024,
            'integrity_ok': integrity_ok
        }
        scalability_results.append(result)
        
        if size >= 1048576:
            size_str = f"{size//1048576}MB"
        else:
            size_str = f"{size//1024}KB"
        print(f"Size: {size_str:>6} | Time: {total_time:>6.3f}s | Throughput: {throughput/1024:>7.1f} KB/s | {('✓' if integrity_ok else '✗')}")
    
    # Test 4: Edge cases and stress tests
    print(f"\n4. Edge Cases and Stress Tests")
    print("-" * 50)
    
    edge_cases = [
        ("Empty file", b""),
        ("Single byte", b"A"),
        ("Small file", b"Hello World!"),
        ("All zeros", b"\x00" * 1000),
        ("All 0xFF", b"\xFF" * 1000),
        ("Highly repetitive", b"AAAA" * 250),
        ("Binary pattern", bytes([i % 256 for i in range(1000)]))
    ]
    
    edge_results = []
    
    for name, test_data in edge_cases:
        try:
            compressed, metadata = compressor.compress(test_data)
            decompressed = compressor.decompress(compressed, metadata)
            integrity_ok = (test_data == decompressed)
            
            if len(test_data) > 0:
                stats = compressor.get_compression_stats(test_data, compressed)
                ratio = stats['compression_ratio']
            else:
                ratio = 0.0
            
            result = {
                'name': name,
                'size': len(test_data),
                'integrity_ok': integrity_ok,
                'compression_ratio': ratio
            }
            edge_results.append(result)
            
            status = "✓" if integrity_ok else "✗"
            print(f"{status} {name:<20} | Size: {len(test_data):>4}B | Ratio: {ratio:.3f}")
            
        except Exception as e:
            print(f"✗ {name:<20} | ERROR: {str(e)}")
    
    # Summary
    print(f"\n5. Test Summary")
    print("-" * 50)
    
    total_correctness = len(correctness_results)
    passed_correctness = sum(1 for r in correctness_results if r['integrity_ok'])
    
    total_performance = len(performance_results)
    passed_performance = sum(1 for r in performance_results if r['integrity_ok'])
    
    total_edge = len(edge_results)
    passed_edge = sum(1 for r in edge_results if r['integrity_ok'])
    
    print(f"Correctness tests:    {passed_correctness}/{total_correctness} passed ({passed_correctness/total_correctness*100:.1f}%)")
    print(f"Performance tests:    {passed_performance}/{total_performance} passed ({passed_performance/total_performance*100:.1f}%)")
    print(f"Edge case tests:      {passed_edge}/{total_edge} passed ({passed_edge/total_edge*100:.1f}%)")
    
    # Calculate average performance
    avg_comp_throughput = sum(r['compression_throughput_kb_s'] for r in performance_results) / len(performance_results)
    avg_decomp_throughput = sum(r['decompression_throughput_kb_s'] for r in performance_results) / len(performance_results)
    avg_compression_ratio = sum(r['compression_ratio'] for r in performance_results) / len(performance_results)
    
    print(f"\nAverage Performance:")
    print(f"  Compression throughput:   {avg_comp_throughput:.1f} KB/s")
    print(f"  Decompression throughput: {avg_decomp_throughput:.1f} KB/s")
    print(f"  Compression ratio:        {avg_compression_ratio:.3f}")
    
    # Save detailed results
    all_results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'correctness_tests': correctness_results,
        'performance_tests': performance_results,
        'scalability_tests': scalability_results,
        'edge_case_tests': edge_results,
        'summary': {
            'correctness_pass_rate': passed_correctness / total_correctness,
            'performance_pass_rate': passed_performance / total_performance,
            'edge_case_pass_rate': passed_edge / total_edge,
            'avg_compression_throughput_kb_s': avg_comp_throughput,
            'avg_decompression_throughput_kb_s': avg_decomp_throughput,
            'avg_compression_ratio': avg_compression_ratio
        }
    }
    
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nDetailed results saved to: comprehensive_test_results.json")
    
    # Overall result
    overall_success = (passed_correctness == total_correctness and 
                      passed_performance == total_performance and 
                      passed_edge == total_edge)
    
    print(f"\nOverall result: {'✓ SUCCESS' if overall_success else '✗ FAILURE'}")
    
    return overall_success

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
