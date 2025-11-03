#!/usr/bin/env python3
"""
Command Line Interface for Circular Chromosome Compression (CCC) Algorithm

This tool provides a CLI for compressing and decompressing files using the
bio-inspired Circular Chromosome Compression algorithm based on dinoflagellate
circular chromosomes.

Usage:
    python run.py compress input_file output_file [options]
    python run.py decompress input_file output_file [options]
    python run.py analyze input_file [options]
    python run.py benchmark [options]
"""

import sys
import argparse
import os
from pathlib import Path
import time
import json

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor
from utils import helpers


def compress_file(input_path: str, output_path: str, args) -> None:
    """Compress a file using CCC algorithm."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    
    print(f"Compressing '{input_path}' using Circular Chromosome Compression...")
    
    # Initialize compressor
    compressor = CircularChromosomeCompressor(
        chunk_size=args.chunk_size,
        min_pattern_length=args.min_pattern
    )
    
    # Read input file
    with open(input_path, 'rb') as f:
        input_data = f.read()
    
    print(f"Input size: {len(input_data):,} bytes")
    
    # Perform compression
    start_time = time.time()
    compressed_data, metadata = compressor.compress(input_data)
    compression_time = time.time() - start_time
    
    # Save compressed data
    helpers.save_compressed_data(compressed_data, metadata, output_path)
    
    # Calculate statistics
    stats = compressor.get_compression_stats(input_data, compressed_data)
    
    print(f"Compression completed in {compression_time:.2f} seconds")
    print(f"Compressed size: {stats['compressed_size_bytes']:,} bytes")
    print(f"Compression ratio: {stats['compression_ratio']:.4f}")
    print(f"Space savings: {stats['space_savings_percent']:.2f}%")
    print(f"Bits per base: {stats['bits_per_base']:.4f}")
    
    # Generate report if requested
    if args.report:
        report_path = output_path.replace('.ccc', '_report.txt')
        report = helpers.create_compression_report(input_path, output_path, stats, report_path)
        print(f"Compression report saved to: {report_path}")
    
    # Export DNA sequence if requested
    if args.export_dna:
        dna_path = output_path.replace('.ccc', '_dna.fasta')
        # Convert compressed data back to DNA for export
        decompressed_binary = compressor.decompress(compressed_data, metadata)
        dna_seq = compressor.binary_to_dna(decompressed_binary)
        helpers.export_dna_sequence(str(dna_seq), dna_path, 'fasta')
        print(f"DNA sequence exported to: {dna_path}")


def decompress_file(input_path: str, output_path: str, args) -> None:
    """Decompress a CCC-compressed file."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    
    print(f"Decompressing '{input_path}'...")
    
    try:
        # Load compressed data
        compressed_data, metadata = helpers.load_compressed_data(input_path)
        
        # Initialize compressor
        compressor = CircularChromosomeCompressor()
        
        # Perform decompression
        start_time = time.time()
        decompressed_data = compressor.decompress(compressed_data, metadata)
        decompression_time = time.time() - start_time
        
        # Save decompressed data
        with open(output_path, 'wb') as f:
            f.write(decompressed_data)
        
        print(f"Decompression completed in {decompression_time:.2f} seconds")
        print(f"Output size: {len(decompressed_data):,} bytes")
        
        # Verify integrity if original hash is available
        if args.verify and 'original_hash' in metadata:
            current_hash = helpers.calculate_file_hash(output_path)
            if current_hash == metadata['original_hash']:
                print("✓ Integrity verification passed")
            else:
                print("✗ Integrity verification failed")
        
    except Exception as e:
        print(f"Error during decompression: {e}")
        sys.exit(1)


def analyze_file(input_path: str, args) -> None:
    """Analyze a file's compressibility with CCC algorithm."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    
    print(f"Analyzing '{input_path}' for CCC compressibility...")
    
    # Initialize compressor
    compressor = CircularChromosomeCompressor(
        chunk_size=args.chunk_size,
        min_pattern_length=args.min_pattern
    )
    
    # Read and analyze file
    with open(input_path, 'rb') as f:
        input_data = f.read()
    
    print(f"File size: {len(input_data):,} bytes")
    
    # Convert to DNA to analyze sequence properties
    dna_seq = compressor.binary_to_dna(input_data)
    gc_content = helpers.calculate_gc_content(str(dna_seq))
    
    print(f"DNA sequence length: {len(dna_seq):,} bases")
    print(f"GC content: {gc_content:.2f}%")
    
    # Perform test compression for analysis
    compressed_data, metadata = compressor.compress(input_data)
    stats = compressor.get_compression_stats(input_data, compressed_data)
    efficiency = helpers.analyze_compression_efficiency(
        len(input_data), 
        stats['compressed_size_bytes'],
        len(dna_seq)
    )
    
    print("\n=== Compression Analysis ===")
    print(f"Estimated compression ratio: {stats['compression_ratio']:.4f}")
    print(f"Estimated space savings: {stats['space_savings_percent']:.2f}%")
    print(f"Bits per base: {efficiency['bits_per_base']:.4f}")
    print(f"Shannon efficiency: {efficiency['shannon_efficiency_percent']:.2f}%")
    print(f"Theoretical optimal: {'Yes' if efficiency['theoretical_optimal'] else 'No'}")
    
    # DNA synthesis cost estimation
    cost_analysis = helpers.estimate_dna_synthesis_cost(len(dna_seq))
    print("\n=== DNA Synthesis Cost Estimation ===")
    print(f"Estimated synthesis cost: ${cost_analysis['total_cost_usd']:.2f}")
    print(f"Cost per KB of data: ${cost_analysis['cost_per_kb_data']:.2f}")


def run_benchmark(args) -> None:
    """Run performance benchmarks for different data sizes."""
    print("Running CCC Algorithm Performance Benchmark...")
    
    # Initialize compressor
    compressor = CircularChromosomeCompressor(
        chunk_size=args.chunk_size,
        min_pattern_length=args.min_pattern
    )
    
    # Define test data sizes
    test_sizes = args.test_sizes if args.test_sizes else [1024, 4096, 16384, 65536, 262144]  # 1KB to 256KB
    
    def format_size(size):
        if size >= 1048576:
            return f'{size//1048576}MB'
        elif size >= 1024:
            return f'{size//1024}KB'
        else:
            return f'{size}B'
    
    print(f"Testing with data sizes: {[format_size(size) for size in test_sizes]}")
    
    # Run benchmarks
    results = helpers.benchmark_compression_speed(compressor, test_sizes)
    
    print("\n=== Benchmark Results ===")
    print(f"{'Size':<10} {'Comp Time':<12} {'Decomp Time':<14} {'Comp Throughput':<18} {'Integrity':<10}")
    print("-" * 80)
    
    for size, metrics in results.items():
        size_str = format_size(size)
        comp_time = f"{metrics['compression_time_sec']:.3f}s"
        decomp_time = f"{metrics['decompression_time_sec']:.3f}s"
        
        # Format throughput appropriately for large files
        throughput_bytes_sec = metrics['compression_throughput_bytes_sec']
        if throughput_bytes_sec >= 1048576:
            throughput = f"{throughput_bytes_sec/1048576:.1f} MB/s"
        else:
            throughput = f"{throughput_bytes_sec/1024:.1f} KB/s"
            
        integrity = "✓" if metrics['integrity_verified'] else "✗"
        
        print(f"{size_str:<10} {comp_time:<12} {decomp_time:<14} {throughput:<18} {integrity:<10}")
    
    # Save detailed results if requested
    if args.save_benchmark:
        output_file = args.save_benchmark
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed benchmark results saved to: {output_file}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Circular Chromosome Compression (CCC) - Bio-inspired data compression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py compress document.pdf compressed.ccc
  python run.py decompress compressed.ccc document_restored.pdf
  python run.py analyze large_dataset.json --report
  python run.py benchmark --test-sizes 1024 4096 16384
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress a file')
    compress_parser.add_argument('input_file', help='Input file to compress')
    compress_parser.add_argument('output_file', help='Output compressed file (.ccc)')
    compress_parser.add_argument('--chunk-size', type=int, default=1000,
                               help='Chunk size for trans-splicing markers (default: 1000)')
    compress_parser.add_argument('--min-pattern', type=int, default=4,
                               help='Minimum pattern length for DVNP compression (default: 4)')
    compress_parser.add_argument('--report', action='store_true',
                               help='Generate compression report')
    compress_parser.add_argument('--export-dna', action='store_true',
                               help='Export DNA sequence to FASTA format')
    
    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress a file')
    decompress_parser.add_argument('input_file', help='Input compressed file (.ccc)')
    decompress_parser.add_argument('output_file', help='Output decompressed file')
    decompress_parser.add_argument('--verify', action='store_true',
                                 help='Verify file integrity after decompression')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file compressibility')
    analyze_parser.add_argument('input_file', help='Input file to analyze')
    analyze_parser.add_argument('--chunk-size', type=int, default=1000,
                              help='Chunk size for analysis (default: 1000)')
    analyze_parser.add_argument('--min-pattern', type=int, default=4,
                              help='Minimum pattern length for analysis (default: 4)')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run performance benchmarks')
    benchmark_parser.add_argument('--test-sizes', type=int, nargs='+',
                                help='Test data sizes in bytes (default: 1024 4096 16384 65536 262144)')
    benchmark_parser.add_argument('--chunk-size', type=int, default=1000,
                                help='Chunk size for benchmarking (default: 1000)')
    benchmark_parser.add_argument('--min-pattern', type=int, default=4,
                                help='Minimum pattern length for benchmarking (default: 4)')
    benchmark_parser.add_argument('--save-benchmark', type=str,
                                help='Save detailed benchmark results to JSON file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'compress':
            compress_file(args.input_file, args.output_file, args)
        elif args.command == 'decompress':
            decompress_file(args.input_file, args.output_file, args)
        elif args.command == 'analyze':
            analyze_file(args.input_file, args)
        elif args.command == 'benchmark':
            run_benchmark(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
