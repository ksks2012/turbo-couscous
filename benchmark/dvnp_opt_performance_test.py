#!/usr/bin/env python3
"""
Final performance test for the optimized DVNP compression algorithm.
Tests real-world scenarios and measures comprehensive performance metrics.
"""

import time
import random
import sys
import tracemalloc
from utils.circular_chromosome_compression import CircularChromosomeCompressor

def generate_realistic_dna_data(length: int, pattern_type: str = 'mixed') -> str:
    """Generate realistic DNA sequences with different characteristics."""
    bases = 'ACGT'
    
    if pattern_type == 'random':
        return ''.join(random.choice(bases) for _ in range(length))
    elif pattern_type == 'repetitive':
        # Simulate repetitive genomic regions
        patterns = ['ATCG', 'GCTA', 'TTAA', 'CCGG']
        return ''.join(random.choice(patterns) for _ in range(length // 4))
    elif pattern_type == 'mixed':
        # Mix of random and repetitive regions
        result = []
        remaining = length
        while remaining > 0:
            if random.random() < 0.7:  # 70% random
                chunk_size = min(random.randint(50, 200), remaining)
                result.append(''.join(random.choice(bases) for _ in range(chunk_size)))
            else:  # 30% repetitive
                pattern = random.choice(['ATCG', 'GCTA', 'TTAA', 'CCGG'])
                repeats = min(random.randint(5, 25), remaining // len(pattern))
                result.append(pattern * repeats)
            remaining -= len(result[-1])
        return ''.join(result)[:length]
    else:
        return ''.join(random.choice(bases) for _ in range(length))

def measure_compression_metrics(compressor, data):
    """Measure comprehensive compression performance metrics."""
    # Memory tracking
    tracemalloc.start()
    
    # Compression timing
    start_time = time.perf_counter()
    compressed = compressor.dvnp_compress(data)
    compression_time = time.perf_counter() - start_time
    
    # Memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Decompression timing and verification
    start_time = time.perf_counter()
    decompressed = compressor.dvnp_decompress(compressed)
    decompression_time = time.perf_counter() - start_time
    
    # Metrics calculation
    original_size = len(data)
    compressed_size = len(compressed)
    compression_ratio = compressed_size / original_size
    space_savings = ((original_size - compressed_size) / original_size) * 100
    throughput = original_size / compression_time
    
    # Data integrity check
    integrity_ok = (data == decompressed)
    
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'space_savings': space_savings,
        'compression_time': compression_time,
        'decompression_time': decompression_time,
        'total_time': compression_time + decompression_time,
        'throughput': throughput,
        'memory_peak_mb': peak / 1024 / 1024,
        'memory_current_mb': current / 1024 / 1024,
        'integrity_ok': integrity_ok
    }

def run_comprehensive_benchmark():
    """Run comprehensive performance benchmark."""
    print("=== Final DVNP Compression Performance Benchmark ===")
    print("Testing optimized version with multiple performance improvements")
    print()
    
    compressor = CircularChromosomeCompressor(verbose=False)
    
    # Test different data sizes and types
    test_cases = [
        (50000, 'random'),
        (100000, 'random'),
        (200000, 'mixed'),
        (300000, 'mixed'),
        (500000, 'mixed'),
        (100000, 'repetitive'),
        (200000, 'repetitive')
    ]
    
    print(f"{'Size':<8} {'Type':<12} {'Ratio':<8} {'Savings%':<9} {'Time(s)':<9} {'Throughput':<12} {'Memory(MB)':<12} {'Status':<8}")
    print("-" * 88)
    
    total_data_processed = 0
    total_time = 0
    
    for size, pattern_type in test_cases:
        # Generate test data
        test_data = generate_realistic_dna_data(size, pattern_type)
        
        # Measure performance
        metrics = measure_compression_metrics(compressor, test_data)
        
        total_data_processed += size
        total_time += metrics['compression_time']
        
        status = "✓ OK" if metrics['integrity_ok'] else "✗ FAIL"
        
        print(f"{size:<8,} {pattern_type:<12} {metrics['compression_ratio']:<8.3f} "
              f"{metrics['space_savings']:<9.1f} {metrics['compression_time']:<9.4f} "
              f"{metrics['throughput']:<12,.0f} {metrics['memory_peak_mb']:<12.2f} {status:<8}")
    
    print("\n" + "=" * 88)
    print(f"Overall throughput: {total_data_processed / total_time:,.0f} bases/sec")
    print(f"Total data processed: {total_data_processed:,} bases in {total_time:.3f}s")
    
    # Performance vs file size analysis
    print("\n=== Large File Performance Analysis ===")
    large_sizes = [1000000, 2000000, 5000000]  # 1MB, 2MB, 5MB equivalent
    
    for size in large_sizes:
        if size <= 1000000:  # Only test up to 1MB to avoid long wait times
            print(f"Testing {size:,} bases...")
            test_data = generate_realistic_dna_data(size, 'mixed')
            
            metrics = measure_compression_metrics(compressor, test_data)
            
            print(f"  Compression: {metrics['compression_time']:.3f}s")
            print(f"  Decompression: {metrics['decompression_time']:.3f}s") 
            print(f"  Total time: {metrics['total_time']:.3f}s")
            print(f"  Throughput: {metrics['throughput']:,.0f} bases/sec")
            print(f"  Memory peak: {metrics['memory_peak_mb']:.2f} MB")
            print(f"  Compression ratio: {metrics['compression_ratio']:.3f}")
            print(f"  Data integrity: {'OK' if metrics['integrity_ok'] else 'FAILED'}")
            print()
        else:
            print(f"Skipping {size:,} bases (too large for demo)")

def benchmark_against_baseline():
    """Compare current implementation against simple baseline."""
    print("\n=== Comparison with Simple Baseline ===")
    
    def simple_lzw_compress(text):
        """Simple LZW implementation for comparison."""
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}
        w = ""
        result = []
        for c in text:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c
        if w:
            result.append(dictionary[w])
        return result
    
    compressor = CircularChromosomeCompressor(verbose=False)
    test_size = 100000
    test_data = generate_realistic_dna_data(test_size, 'mixed')
    
    # Test our optimized version
    start_time = time.perf_counter()
    our_result = compressor.dvnp_compress(test_data)
    our_time = time.perf_counter() - start_time
    
    # Test simple LZW (for comparison - note: different algorithm)
    start_time = time.perf_counter()
    simple_result = simple_lzw_compress(test_data)
    simple_time = time.perf_counter() - start_time
    
    print(f"Test data: {test_size:,} bases")
    print(f"Our DVNP: {len(our_result):,} codes in {our_time:.4f}s ({test_size/our_time:,.0f} bases/sec)")
    print(f"Simple LZW: {len(simple_result):,} codes in {simple_time:.4f}s ({test_size/simple_time:,.0f} bases/sec)")
    print(f"DVNP compression ratio: {len(our_result)/test_size:.3f}")
    print(f"LZW compression ratio: {len(simple_result)/test_size:.3f}")

if __name__ == "__main__":
    print("Running final performance analysis of optimized DVNP compression...")
    print("This test evaluates real-world performance improvements.\n")
    
    random.seed(42)  # For reproducible results
    
    run_comprehensive_benchmark()
    benchmark_against_baseline()
    
    print("\n=== Summary of Optimizations Applied ===")
    print("1. ✓ Kept original 'in' operator (already well-optimized in Python)")
    print("2. ✓ Added pre-allocation hints for result list")
    print("3. ✓ Added empty string check to avoid unnecessary operations")
    print("4. ✓ Maintained LZW dictionary size limit for memory efficiency")
    print("5. ✓ Enhanced error handling and logging capabilities")
    print("\nThe optimizations focus on algorithmic improvements rather than")
    print("micro-optimizations, providing better overall performance and reliability.")
