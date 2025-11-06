#!/usr/bin/env python3
"""
Comprehensive Dictionary Reset Test Suite for CCC Algorithm.

This module provides a complete test suite for the dynamic dictionary reset
functionality, including unit tests, integration tests, and performance benchmarks.
"""

import time
import random
from typing import List, Dict, Tuple
from utils.circular_chromosome_compression import CircularChromosomeCompressor

class DictionaryResetTester:
    """Test suite for dictionary reset functionality."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the test suite."""
        self.verbose = verbose
        self.compressor = CircularChromosomeCompressor(verbose=verbose)
        self.results = []
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[TEST] {message}")
    
    def generate_test_sequence(self, length: int, pattern_type: str = 'mixed') -> str:
        """Generate test DNA sequences with different characteristics."""
        bases = 'ACGT'
        
        if pattern_type == 'random':
            return ''.join(random.choice(bases) for _ in range(length))
        
        elif pattern_type == 'repetitive':
            pattern = 'ATCGATCG'
            return (pattern * (length // len(pattern) + 1))[:length]
        
        elif pattern_type == 'changing_patterns':
            # Multiple different repetitive regions that change over time
            patterns = ['ATCGATCG', 'GCTAGCTA', 'TTAATTAA', 'CCGGCCGG']
            sequence = []
            chunk_size = length // len(patterns)
            
            for pattern in patterns:
                chunk = (pattern * (chunk_size // len(pattern) + 1))[:chunk_size]
                sequence.append(chunk)
            
            return ''.join(sequence)[:length]
        
        elif pattern_type == 'genomic':
            # Realistic genomic sequence with various patterns
            sequence = []
            remaining = length
            
            while remaining > 0:
                pattern_choice = random.choice(['random', 'tandem', 'microsatellite'])
                
                if pattern_choice == 'random':
                    chunk_size = min(random.randint(100, 1000), remaining)
                    chunk = ''.join(random.choice(bases) for _ in range(chunk_size))
                
                elif pattern_choice == 'tandem':
                    repeat_unit = ''.join(random.choice(bases) for _ in range(random.randint(3, 10)))
                    chunk_size = min(random.randint(200, 2000), remaining)
                    repeats = chunk_size // len(repeat_unit)
                    chunk = repeat_unit * repeats
                
                else:  # microsatellite
                    unit_size = random.randint(2, 6)
                    repeat_unit = ''.join(random.choice(bases) for _ in range(unit_size))
                    chunk_size = min(random.randint(100, 500), remaining)
                    repeats = chunk_size // unit_size
                    chunk = repeat_unit * repeats
                
                sequence.append(chunk)
                remaining -= len(chunk)
            
            return ''.join(sequence)[:length]
        
        else:  # mixed
            # Combination of different patterns
            parts = []
            part_length = length // 4
            
            parts.append(self.generate_test_sequence(part_length, 'random'))
            parts.append(self.generate_test_sequence(part_length, 'repetitive'))
            parts.append(self.generate_test_sequence(part_length, 'changing_patterns'))
            parts.append(self.generate_test_sequence(length - 3 * part_length, 'genomic'))
            
            return ''.join(parts)
    
    def test_basic_reset_functionality(self) -> bool:
        """Test basic dictionary reset functionality with manual reset markers."""
        print("=== Basic Reset Functionality Test ===")
        
        # Test 1: Simple sequence without reset
        test_seq = "ATCGATCGATCG"
        compressed = self.compressor.dvnp_compress(test_seq)
        decompressed = self.compressor.dvnp_decompress(compressed)
        
        basic_test = test_seq == decompressed
        self._log(f"Basic compression test: {'PASS' if basic_test else 'FAIL'}")
        
        # Test 2: Manual reset marker test
        manual_compressed = [0, 3, 1, 2, 65535, 0, 3, 1, 2]  # AT CG RESET AT CG
        expected = "ATCGATCG"
        manual_decompressed = self.compressor.dvnp_decompress(manual_compressed)
        
        manual_test = expected == manual_decompressed
        self._log(f"Manual reset marker test: {'PASS' if manual_test else 'FAIL'}")
        
        # Test 3: Multiple reset markers
        multi_reset = [0, 3, 65535, 1, 2, 65535, 0, 1]  # AT RESET CG RESET AC
        expected_multi = "ATCGAC"
        multi_decompressed = self.compressor.dvnp_decompress(multi_reset)
        
        multi_test = expected_multi == multi_decompressed
        self._log(f"Multiple reset markers test: {'PASS' if multi_test else 'FAIL'}")
        
        overall_result = basic_test and manual_test and multi_test
        print(f"Basic functionality: {'✓ PASS' if overall_result else '✗ FAIL'}")
        print()
        
        return overall_result
    
    def test_large_sequence_reset(self) -> Dict:
        """Test dictionary reset with large sequences that trigger automatic resets."""
        print("=== Large Sequence Reset Test ===")
        
        results = {}
        test_sizes = [100000, 500000, 1000000, 2000000]
        
        for size in test_sizes:
            self._log(f"Testing {size:,} base sequence...")
            
            # Generate test sequence with changing patterns to trigger resets
            test_sequence = self.generate_test_sequence(size, 'changing_patterns')
            
            # Track reset count
            original_log = self.compressor._log
            reset_count = 0
            
            def counting_log(message):
                nonlocal reset_count
                if "Dictionary reset" in message:
                    reset_count += 1
                if self.verbose:
                    original_log(message)
            
            self.compressor._log = counting_log
            
            # Test compression and decompression
            start_time = time.perf_counter()
            compressed = self.compressor.dvnp_compress(test_sequence)
            compression_time = time.perf_counter() - start_time
            
            start_time = time.perf_counter()
            decompressed = self.compressor.dvnp_decompress(compressed)
            decompression_time = time.perf_counter() - start_time
            
            # Restore original log
            self.compressor._log = original_log
            
            # Calculate metrics
            integrity = test_sequence == decompressed
            compression_ratio = len(compressed) / len(test_sequence)
            throughput = size / (compression_time + decompression_time)
            
            results[size] = {
                'reset_count': reset_count,
                'compression_ratio': compression_ratio,
                'integrity': integrity,
                'throughput': throughput,
                'compression_time': compression_time,
                'decompression_time': decompression_time
            }
            
            status = "✓ PASS" if integrity else "✗ FAIL"
            print(f"Size: {size:>8,} | Resets: {reset_count:>2} | Ratio: {compression_ratio:.3f} | {status}")
        
        print()
        return results
    
    def test_reset_effectiveness(self) -> Dict:
        """Compare compression effectiveness with and without reset capability."""
        print("=== Reset Effectiveness Comparison ===")
        
        # Create a compressor without reset for comparison
        class NoResetCompressor(CircularChromosomeCompressor):
            def dvnp_compress(self, dna_seq: str) -> List[int]:
                """DVNP compression without dictionary reset."""
                if not self._validate_input(dna_seq, "dna_seq"):
                    return []
                
                dictionary = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
                next_code = 4
                current = ''
                result = []
                
                for ch in dna_seq:
                    combined = current + ch
                    if combined in dictionary:
                        current = combined
                    else:
                        if current:
                            result.append(dictionary[current])
                        # No reset - just stop adding when full
                        if next_code < 65536:
                            dictionary[combined] = next_code
                            next_code += 1
                        current = ch
                
                if current:
                    result.append(dictionary[current])
                
                return result
        
        no_reset_compressor = NoResetCompressor(verbose=False)
        
        # Test different sequence types
        test_cases = [
            ('changing_patterns', 500000),
            ('genomic', 300000),
            ('repetitive', 200000)
        ]
        
        results = {}
        
        for pattern_type, size in test_cases:
            test_sequence = self.generate_test_sequence(size, pattern_type)
            
            # Test with reset
            start_time = time.perf_counter()
            with_reset = self.compressor.dvnp_compress(test_sequence)
            reset_time = time.perf_counter() - start_time
            
            # Test without reset
            start_time = time.perf_counter()
            without_reset = no_reset_compressor.dvnp_compress(test_sequence)
            no_reset_time = time.perf_counter() - start_time
            
            # Calculate improvement
            reset_ratio = len(with_reset) / size
            no_reset_ratio = len(without_reset) / size
            improvement = ((no_reset_ratio - reset_ratio) / no_reset_ratio) * 100 if no_reset_ratio > 0 else 0
            
            results[pattern_type] = {
                'reset_ratio': reset_ratio,
                'no_reset_ratio': no_reset_ratio,
                'improvement_percent': improvement,
                'reset_time': reset_time,
                'no_reset_time': no_reset_time
            }
            
            print(f"{pattern_type:>16}: Reset {reset_ratio:.3f} vs No-Reset {no_reset_ratio:.3f} "
                  f"(Improvement: {improvement:+.1f}%)")
        
        print()
        return results
    
    def test_performance_benchmarks(self) -> Dict:
        """Performance benchmarks for different sequence sizes and types."""
        print("=== Performance Benchmarks ===")
        
        benchmarks = {}
        test_configurations = [
            ('small', 50000, 'mixed'),
            ('medium', 200000, 'genomic'),
            ('large', 1000000, 'changing_patterns'),
            ('xlarge', 5000000, 'mixed')
        ]
        
        print(f"{'Config':<8} {'Size':<8} {'Comp Time':<10} {'Decomp Time':<12} {'Throughput':<12} {'Ratio':<8}")
        print("-" * 70)
        
        for config_name, size, pattern in test_configurations:
            test_sequence = self.generate_test_sequence(size, pattern)
            
            # Compression benchmark
            start_time = time.perf_counter()
            compressed = self.compressor.dvnp_compress(test_sequence)
            comp_time = time.perf_counter() - start_time
            
            # Decompression benchmark
            start_time = time.perf_counter()
            decompressed = self.compressor.dvnp_decompress(compressed)
            decomp_time = time.perf_counter() - start_time
            
            # Calculate metrics
            total_time = comp_time + decomp_time
            throughput = size / total_time if total_time > 0 else 0
            ratio = len(compressed) / size
            integrity = test_sequence == decompressed
            
            benchmarks[config_name] = {
                'size': size,
                'compression_time': comp_time,
                'decompression_time': decomp_time,
                'throughput': throughput,
                'ratio': ratio,
                'integrity': integrity
            }
            
            status = "✓" if integrity else "✗"
            print(f"{config_name:<8} {size:<8,} {comp_time:<10.3f} {decomp_time:<12.3f} "
                  f"{throughput/1000:<12.1f} {ratio:<8.3f} {status}")
        
        print()
        return benchmarks
    
    def test_edge_cases(self) -> Dict:
        """Test edge cases and error handling."""
        print("=== Edge Cases Test ===")
        
        edge_results = {}
        
        # Test cases
        test_cases = [
            ("Empty sequence", ""),
            ("Single base", "A"),
            ("Very short", "ATCG"),
            ("All same base", "A" * 1000),
            ("Alternating", "ATATATATATAT" * 100),
            ("Complex pattern", "ATCGATCGATCG" * 500)
        ]
        
        for test_name, sequence in test_cases:
            try:
                compressed = self.compressor.dvnp_compress(sequence)
                decompressed = self.compressor.dvnp_decompress(compressed)
                
                integrity = sequence == decompressed
                ratio = len(compressed) / len(sequence) if len(sequence) > 0 else 0
                
                edge_results[test_name] = {
                    'integrity': integrity,
                    'ratio': ratio,
                    'original_length': len(sequence),
                    'compressed_length': len(compressed)
                }
                
                status = "✓ PASS" if integrity else "✗ FAIL"
                print(f"{test_name:<20}: {status} (Ratio: {ratio:.3f})")
                
            except Exception as e:
                edge_results[test_name] = {'error': str(e)}
                print(f"{test_name:<20}: ✗ ERROR - {e}")
        
        print()
        return edge_results
    
    def run_comprehensive_test_suite(self) -> Dict:
        """Run the complete test suite and return results."""
        print("=" * 60)
        print("Dictionary Reset Comprehensive Test Suite")
        print("=" * 60)
        print()
        
        # Set random seed for reproducible results
        random.seed(42)
        
        # Run all tests
        basic_result = self.test_basic_reset_functionality()
        large_sequence_results = self.test_large_sequence_reset()
        effectiveness_results = self.test_reset_effectiveness()
        performance_results = self.test_performance_benchmarks()
        edge_case_results = self.test_edge_cases()
        
        # Compile overall results
        overall_results = {
            'basic_functionality': basic_result,
            'large_sequences': large_sequence_results,
            'effectiveness_comparison': effectiveness_results,
            'performance_benchmarks': performance_results,
            'edge_cases': edge_case_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        basic_status = "✓ PASS" if basic_result else "✗ FAIL"
        print(f"Basic Functionality:     {basic_status}")
        
        large_pass = sum(1 for r in large_sequence_results.values() if r['integrity'])
        large_total = len(large_sequence_results)
        print(f"Large Sequence Tests:    {large_pass}/{large_total} passed")
        
        edge_pass = sum(1 for r in edge_case_results.values() if r.get('integrity', False))
        edge_total = len(edge_case_results)
        print(f"Edge Case Tests:         {edge_pass}/{edge_total} passed")
        
        perf_pass = sum(1 for r in performance_results.values() if r['integrity'])
        perf_total = len(performance_results)
        print(f"Performance Tests:       {perf_pass}/{perf_total} passed")
        
        # Overall success
        overall_success = (basic_result and 
                          large_pass == large_total and 
                          perf_pass == perf_total)
        
        print()
        print(f"Overall Result: {'✓ SUCCESS' if overall_success else '✗ FAILURE'}")
        
        if overall_success:
            print("🎉 All dictionary reset tests passed successfully!")
        else:
            print("❌ Some tests failed. Please review the results above.")
        
        print()
        return overall_results

def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dictionary Reset Test Suite')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-q', '--quick', action='store_true', help='Run only basic tests')
    args = parser.parse_args()
    
    tester = DictionaryResetTester(verbose=args.verbose)
    
    if args.quick:
        print("Running quick test suite...")
        basic_result = tester.test_basic_reset_functionality()
        edge_results = tester.test_edge_cases()
        
        print("Quick Test Summary:")
        print(f"Basic: {'PASS' if basic_result else 'FAIL'}")
        edge_pass = sum(1 for r in edge_results.values() if r.get('integrity', False))
        print(f"Edge Cases: {edge_pass}/{len(edge_results)} passed")
    else:
        results = tester.run_comprehensive_test_suite()
        
        # Save results if needed
        try:
            import json
            with open('dictionary_reset_test_results.json', 'w') as f:
                # Convert results to JSON-serializable format
                json_results = {}
                for key, value in results.items():
                    if isinstance(value, dict):
                        json_results[key] = value
                    else:
                        json_results[key] = str(value)
                
                json.dump(json_results, f, indent=2)
            print(f"Detailed results saved to: dictionary_reset_test_results.json")
        except ImportError:
            pass

if __name__ == "__main__":
    main()
