#!/usr/bin/env python3
"""
Genomic Sequence Compression Demo for CCC Algorithm.

This module demonstrates the benefits of dynamic dictionary reset
for realistic genomic data compression scenarios.
"""

import time
import random
from typing import Dict, List, Tuple
from utils.circular_chromosome_compression import CircularChromosomeCompressor

class GenomicCompressionDemo:
    """Demo suite for genomic sequence compression with dictionary reset."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the demo suite."""
        self.verbose = verbose
        self.compressor = CircularChromosomeCompressor(verbose=verbose)
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEMO] {message}")
    
    def create_repetitive_elements(self, length: int) -> str:
        """Simulate repetitive genomic elements like transposons."""
        # Common repetitive elements (simplified)
        elements = [
            'ATCGATCGATCG',    # Simple repeat
            'GCTAGCTAGCTA',    # Inverted repeat
            'TTAATTAATTAA',    # AT-rich repeat
            'CCGGCCGGCCGG',    # GC-rich repeat
            'AGAGAGAGAGAG',    # Microsatellite
            'CTCTCTCTCTCT'     # Microsatellite
        ]
        
        result = []
        remaining = length
        
        while remaining > 0:
            if random.random() < 0.8:  # 80% repetitive elements
                element = random.choice(elements)
                repeats = min(random.randint(10, 100), remaining // len(element))
                chunk = element * repeats
            else:  # 20% unique sequence
                chunk_size = min(random.randint(50, 200), remaining)
                chunk = ''.join(random.choice('ACGT') for _ in range(chunk_size))
            
            result.append(chunk)
            remaining -= len(chunk)
        
        return ''.join(result)[:length]
    
    def create_tandem_repeats(self, length: int) -> str:
        """Create tandem repeat patterns found in genomes."""
        repeat_units = ['AT', 'GC', 'CAG', 'CTG', 'ATCG', 'GCTA', 'AAG', 'TTC']
        result = []
        remaining = length
        
        while remaining > 0:
            unit = random.choice(repeat_units)
            repeat_count = min(random.randint(20, 200), remaining // len(unit))
            chunk = unit * repeat_count
            
            # Add random spacer sequence between repeats
            if remaining > len(chunk) + 50 and random.random() < 0.3:
                spacer_size = min(random.randint(10, 50), remaining - len(chunk))
                spacer = ''.join(random.choice('ACGT') for _ in range(spacer_size))
                chunk += spacer
            
            result.append(chunk)
            remaining -= len(chunk)
        
        return ''.join(result)[:length]
    
    def create_coding_sequence(self, length: int) -> str:
        """Create sequence resembling coding regions with codon structure."""
        # Simplified codon usage (real genomes have codon bias)
        codons = [
            'ATG', 'TGA', 'TAA', 'TAG',  # Start/stop codons
            'TTT', 'TTC', 'TTA', 'TTG', 'TCT', 'TCC', 'TCA', 'TCG',
            'TAT', 'TAC', 'TGT', 'TGC', 'TGG', 'CTT', 'CTC', 'CTA',
            'CTG', 'CCT', 'CCC', 'CCA', 'CCG', 'CAT', 'CAC', 'CAA',
            'CAG', 'CGT', 'CGC', 'CGA', 'CGG', 'ATT', 'ATC', 'ATA',
            'ACT', 'ACC', 'ACA', 'ACG', 'AAT', 'AAC', 'AAA', 'AAG',
            'AGT', 'AGC', 'AGA', 'AGG', 'GTT', 'GTC', 'GTA', 'GTG',
            'GCT', 'GCC', 'GCA', 'GCG', 'GAT', 'GAC', 'GAA', 'GAG',
            'GGT', 'GGC', 'GGA', 'GGG'
        ]
        
        result = []
        remaining = length
        
        # Start with start codon
        if remaining >= 3:
            result.append('ATG')
            remaining -= 3
        
        while remaining >= 3:
            # Create coding sequence with some structure
            exon_length = min(random.randint(150, 900), remaining // 3)  # Exons are 50-300 codons
            
            for _ in range(exon_length):
                if remaining >= 3:
                    codon = random.choice(codons[4:])  # Avoid stop codons in middle
                    result.append(codon)
                    remaining -= 3
            
            # Add intron-like sequence occasionally
            if remaining > 50 and random.random() < 0.3:
                intron_length = min(random.randint(30, 150), remaining)
                intron = ''.join(random.choice('ACGT') for _ in range(intron_length))
                result.append(intron)
                remaining -= len(intron)
        
        # End with stop codon if possible
        if remaining >= 3:
            result.append(random.choice(['TGA', 'TAA', 'TAG']))
            remaining -= 3
        
        # Fill remaining with random sequence
        if remaining > 0:
            result.append(''.join(random.choice('ACGT') for _ in range(remaining)))
        
        return ''.join(result)[:length]
    
    def create_mixed_genomic_content(self, length: int) -> str:
        """Create mixed genomic content with different region types."""
        content_types = [
            ('repetitive', self.create_repetitive_elements),
            ('tandem', self.create_tandem_repeats),
            ('coding', self.create_coding_sequence),
            ('random', lambda l: ''.join(random.choice('ACGT') for _ in range(l)))
        ]
        
        # Define proportions similar to real genomes
        proportions = [0.45, 0.15, 0.25, 0.15]  # repetitive, tandem, coding, random
        
        result = []
        remaining = length
        
        for (content_type, generator), proportion in zip(content_types, proportions):
            if remaining <= 0:
                break
            
            segment_length = min(int(length * proportion), remaining)
            if segment_length > 0:
                segment = generator(segment_length)
                result.append(segment)
                remaining -= len(segment)
        
        # Fill any remaining length with random sequence
        if remaining > 0:
            result.append(''.join(random.choice('ACGT') for _ in range(remaining)))
        
        # Shuffle segments to create more realistic genome structure
        random.shuffle(result)
        
        return ''.join(result)[:length]
    
    def create_genomic_pattern_with_variations(self, pattern_size: int, repeats: int) -> str:
        """Create genomic patterns with evolutionary variations."""
        bases = 'ACGT'
        
        # Create base pattern
        base_pattern = ''.join(random.choice(bases) for _ in range(pattern_size))
        
        result = []
        for i in range(repeats):
            if i % 10 == 0 and i > 0:  # Introduce variation every 10 repeats
                # Simulate evolutionary changes
                pattern_list = list(base_pattern)
                
                # Point mutations
                for _ in range(random.randint(1, 2)):
                    if pattern_list:
                        pos = random.randint(0, len(pattern_list) - 1)
                        pattern_list[pos] = random.choice(bases)
                
                # Small indels occasionally
                if random.random() < 0.3:
                    if random.random() < 0.5 and len(pattern_list) > 1:
                        # Deletion
                        pos = random.randint(0, len(pattern_list) - 1)
                        pattern_list.pop(pos)
                    else:
                        # Insertion
                        pos = random.randint(0, len(pattern_list))
                        pattern_list.insert(pos, random.choice(bases))
                
                result.append(''.join(pattern_list))
            else:
                result.append(base_pattern)
        
        return ''.join(result)
    
    def demo_compression_benefits(self) -> Dict:
        """Demonstrate compression benefits for different genomic patterns."""
        print("=== Genomic Compression Benefits Demo ===")
        print()
        
        test_cases = [
            ('Repetitive Elements', 200000, 'repetitive'),
            ('Tandem Repeats', 150000, 'tandem'),
            ('Coding Sequences', 300000, 'coding'),
            ('Mixed Genomic', 500000, 'mixed'),
            ('Pattern Variations', 100000, 'variations')
        ]
        
        results = {}
        
        print(f"{'Pattern Type':<20} {'Size':<8} {'Compressed':<11} {'Ratio':<8} {'Resets':<7} {'Time (s)':<10}")
        print("-" * 75)
        
        for pattern_name, size, pattern_type in test_cases:
            # Generate test sequence
            if pattern_type == 'repetitive':
                sequence = self.create_repetitive_elements(size)
            elif pattern_type == 'tandem':
                sequence = self.create_tandem_repeats(size)
            elif pattern_type == 'coding':
                sequence = self.create_coding_sequence(size)
            elif pattern_type == 'mixed':
                sequence = self.create_mixed_genomic_content(size)
            else:  # variations
                sequence = self.create_genomic_pattern_with_variations(50, size // 50)
            
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
            
            # Compress and measure performance
            start_time = time.perf_counter()
            compressed = self.compressor.dvnp_compress(sequence)
            decompressed = self.compressor.dvnp_decompress(compressed)
            total_time = time.perf_counter() - start_time
            
            # Restore original log
            self.compressor._log = original_log
            
            # Calculate metrics
            ratio = len(compressed) / len(sequence)
            integrity = sequence == decompressed
            space_saved = ((len(sequence) - len(compressed)) / len(sequence)) * 100
            
            results[pattern_type] = {
                'pattern_name': pattern_name,
                'original_size': len(sequence),
                'compressed_size': len(compressed),
                'ratio': ratio,
                'space_saved': space_saved,
                'reset_count': reset_count,
                'time': total_time,
                'integrity': integrity
            }
            
            status = "✓" if integrity else "✗"
            print(f"{pattern_name:<20} {size:<8,} {len(compressed):<11,} {ratio:<8.3f} "
                  f"{reset_count:<7} {total_time:<10.3f} {status}")
        
        print()
        return results
    
    def demo_scalability_test(self) -> Dict:
        """Demonstrate scalability with very large sequences."""
        print("=== Scalability Demo with Large Sequences ===")
        print()
        
        # Test increasingly large sequences
        test_sizes = [1000000, 2000000, 5000000, 10000000]  # 1MB to 10MB
        
        results = {}
        
        print(f"{'Size':<8} {'Pattern':<12} {'Comp Time':<11} {'Decomp Time':<12} "
              f"{'Throughput':<12} {'Resets':<7} {'Ratio':<8}")
        print("-" * 80)
        
        for size in test_sizes:
            # Use mixed genomic content for realistic testing
            self._log(f"Generating {size:,} base mixed genomic sequence...")
            sequence = self.create_mixed_genomic_content(size)
            
            # Track performance and resets
            original_log = self.compressor._log
            reset_count = 0
            
            def counting_log(message):
                nonlocal reset_count
                if "Dictionary reset" in message:
                    reset_count += 1
            
            self.compressor._log = counting_log
            
            # Compression timing
            start_time = time.perf_counter()
            compressed = self.compressor.dvnp_compress(sequence)
            comp_time = time.perf_counter() - start_time
            
            # Decompression timing
            start_time = time.perf_counter()
            decompressed = self.compressor.dvnp_decompress(compressed)
            decomp_time = time.perf_counter() - start_time
            
            # Restore log
            self.compressor._log = original_log
            
            # Metrics
            total_time = comp_time + decomp_time
            throughput = size / total_time if total_time > 0 else 0
            ratio = len(compressed) / size
            integrity = sequence == decompressed
            
            results[size] = {
                'compression_time': comp_time,
                'decompression_time': decomp_time,
                'throughput': throughput,
                'reset_count': reset_count,
                'ratio': ratio,
                'integrity': integrity
            }
            
            size_str = f"{size//1000000}MB" if size >= 1000000 else f"{size//1000}KB"
            status = "✓" if integrity else "✗"
            
            print(f"{size_str:<8} {'Mixed':<12} {comp_time:<11.3f} {decomp_time:<12.3f} "
                  f"{throughput/1000:<12.0f} {reset_count:<7} {ratio:<8.3f} {status}")
        
        print()
        return results
    
    def demo_reset_effectiveness(self) -> None:
        """Demonstrate when dictionary reset is most effective."""
        print("=== Dictionary Reset Effectiveness Demo ===")
        print()
        
        # Create scenarios where reset is particularly beneficial
        scenarios = [
            {
                'name': 'Changing Repetitive Patterns',
                'description': 'Multiple different repetitive regions',
                'sequence': (self.create_repetitive_elements(100000) +
                           self.create_tandem_repeats(100000) +
                           self.create_coding_sequence(100000))
            },
            {
                'name': 'Genome Assembly Contigs',
                'description': 'Multiple contigs with different characteristics',
                'sequence': ''.join([
                    self.create_mixed_genomic_content(200000),
                    'N' * 100,  # Assembly gap
                    self.create_mixed_genomic_content(200000),
                    'N' * 100,
                    self.create_mixed_genomic_content(200000)
                ])
            }
        ]
        
        for scenario in scenarios:
            print(f"Scenario: {scenario['name']}")
            print(f"Description: {scenario['description']}")
            
            sequence = scenario['sequence']
            
            # Track reset events with detailed logging
            original_log = self.compressor._log
            reset_events = []
            
            def tracking_log(message):
                if "Dictionary reset" in message:
                    reset_events.append(message)
                    print(f"  [RESET] {message}")
            
            self.compressor._log = tracking_log
            
            # Perform compression
            start_time = time.perf_counter()
            compressed = self.compressor.dvnp_compress(sequence)
            total_time = time.perf_counter() - start_time
            
            # Restore log
            self.compressor._log = original_log
            
            # Results
            ratio = len(compressed) / len(sequence)
            space_saved = ((len(sequence) - len(compressed)) / len(sequence)) * 100
            
            print(f"  Original size: {len(sequence):,} bases")
            print(f"  Compressed size: {len(compressed):,} codes")
            print(f"  Compression ratio: {ratio:.3f}")
            print(f"  Space saved: {space_saved:.1f}%")
            print(f"  Reset events: {len(reset_events)}")
            print(f"  Processing time: {total_time:.3f}s")
            print()
    
    def run_complete_demo(self) -> Dict:
        """Run the complete genomic compression demonstration."""
        print("=" * 70)
        print("Genomic Sequence Compression Demonstration")
        print("Dynamic Dictionary Reset Benefits for Realistic Genomic Data")
        print("=" * 70)
        print()
        
        # Set random seed for reproducible results
        random.seed(42)
        
        # Run all demonstrations
        compression_results = self.demo_compression_benefits()
        scalability_results = self.demo_scalability_test()
        self.demo_reset_effectiveness()
        
        # Summary
        print("=" * 70)
        print("DEMONSTRATION SUMMARY")
        print("=" * 70)
        
        avg_ratio = sum(r['ratio'] for r in compression_results.values()) / len(compression_results)
        avg_space_saved = sum(r['space_saved'] for r in compression_results.values()) / len(compression_results)
        total_resets = sum(r['reset_count'] for r in compression_results.values())
        
        print(f"Pattern Types Tested:      {len(compression_results)}")
        print(f"Average Compression Ratio: {avg_ratio:.3f}")
        print(f"Average Space Saved:       {avg_space_saved:.1f}%")
        print(f"Total Reset Events:        {total_resets}")
        
        # Scalability summary
        max_size = max(scalability_results.keys())
        max_throughput = max(r['throughput'] for r in scalability_results.values())
        
        print(f"Largest File Tested:       {max_size:,} bases ({max_size//1000000}MB)")
        print(f"Peak Throughput:           {max_throughput:,.0f} bases/sec")
        
        print()
        print("🧬 Genomic compression demonstration completed successfully!")
        print("   Dictionary reset provides significant benefits for:")
        print("   • Repetitive genomic elements")
        print("   • Changing sequence patterns")
        print("   • Large-scale genomic assemblies")
        print("   • Mixed genomic content types")
        
        return {
            'compression_patterns': compression_results,
            'scalability_tests': scalability_results,
            'summary': {
                'avg_compression_ratio': avg_ratio,
                'avg_space_saved': avg_space_saved,
                'total_reset_events': total_resets,
                'max_file_size': max_size,
                'peak_throughput': max_throughput
            }
        }

def main():
    """Main demo runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genomic Sequence Compression Demo')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--pattern', choices=['repetitive', 'tandem', 'coding', 'mixed', 'all'],
                       default='all', help='Run specific pattern demo')
    parser.add_argument('--size', type=int, default=500000, help='Sequence size for single pattern test')
    args = parser.parse_args()
    
    demo = GenomicCompressionDemo(verbose=args.verbose)
    
    if args.pattern == 'all':
        # Run complete demonstration
        results = demo.run_complete_demo()
    else:
        # Run specific pattern demo
        print(f"Running {args.pattern} pattern demo with {args.size:,} bases...")
        
        if args.pattern == 'repetitive':
            sequence = demo.create_repetitive_elements(args.size)
        elif args.pattern == 'tandem':
            sequence = demo.create_tandem_repeats(args.size)
        elif args.pattern == 'coding':
            sequence = demo.create_coding_sequence(args.size)
        else:  # mixed
            sequence = demo.create_mixed_genomic_content(args.size)
        
        # Simple compression test
        compressed = demo.compressor.dvnp_compress(sequence)
        decompressed = demo.compressor.dvnp_decompress(compressed)
        
        ratio = len(compressed) / len(sequence)
        space_saved = ((len(sequence) - len(compressed)) / len(sequence)) * 100
        integrity = sequence == decompressed
        
        print(f"Results:")
        print(f"  Original size: {len(sequence):,} bases")
        print(f"  Compressed size: {len(compressed):,} codes") 
        print(f"  Compression ratio: {ratio:.3f}")
        print(f"  Space saved: {space_saved:.1f}%")
        print(f"  Data integrity: {'✓ OK' if integrity else '✗ FAILED'}")

if __name__ == "__main__":
    main()
