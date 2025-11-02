"""
Utility functions for the Circular Chromosome Compression algorithm.
Provides helper functions for data validation, analysis, and processing.
"""

import os
import json
import pickle
from typing import Any, Dict, List, Optional, Tuple
import hashlib
from pathlib import Path


def validate_dna_sequence(sequence: str) -> bool:
    """
    Validate that a sequence contains only valid DNA bases.
    
    Args:
        sequence: DNA sequence string to validate
        
    Returns:
        True if sequence is valid, False otherwise
    """
    valid_bases = set('ACGT')
    return all(base.upper() in valid_bases for base in sequence)


def calculate_gc_content(sequence: str) -> float:
    """
    Calculate GC content percentage of DNA sequence.
    
    Args:
        sequence: DNA sequence string
        
    Returns:
        GC content as percentage (0-100)
    """
    if not sequence:
        return 0.0
    
    gc_count = sequence.upper().count('G') + sequence.upper().count('C')
    return (gc_count / len(sequence)) * 100


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file for integrity checking.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', etc.)
        
    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def save_compressed_data(compressed_data: List[int], metadata: Dict, output_path: str) -> None:
    """
    Save compressed data and metadata to file.
    
    Args:
        compressed_data: Compressed data list
        metadata: Compression metadata dictionary
        output_path: Output file path
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    data_to_save = {
        'compressed_data': compressed_data,
        'metadata': metadata,
        'version': '1.0',
        'algorithm': 'CCC'
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(data_to_save, f)


def load_compressed_data(input_path: str) -> Tuple[List[int], Dict]:
    """
    Load compressed data and metadata from file.
    
    Args:
        input_path: Input file path
        
    Returns:
        Tuple of (compressed_data, metadata)
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is invalid
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'rb') as f:
        data = pickle.load(f)
    
    if not isinstance(data, dict) or 'compressed_data' not in data or 'metadata' not in data:
        raise ValueError("Invalid compressed file format")
    
    return data['compressed_data'], data['metadata']


def export_dna_sequence(sequence: str, output_path: str, format: str = 'fasta') -> None:
    """
    Export DNA sequence to standard bioinformatics format.
    
    Args:
        sequence: DNA sequence string
        output_path: Output file path
        format: Output format ('fasta', 'raw')
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_path, 'w') as f:
        if format.lower() == 'fasta':
            f.write(f">CCC_Compressed_Sequence\n")
            # Write sequence in 80-character lines (standard FASTA format)
            for i in range(0, len(sequence), 80):
                f.write(f"{sequence[i:i+80]}\n")
        else:  # raw format
            f.write(sequence)


def analyze_compression_efficiency(original_size: int, compressed_size: int, 
                                 dna_length: int) -> Dict[str, float]:
    """
    Analyze compression efficiency with various metrics.
    
    Args:
        original_size: Original data size in bytes
        compressed_size: Compressed data size in bytes
        dna_length: Length of DNA sequence
        
    Returns:
        Dictionary with efficiency metrics
    """
    if original_size == 0:
        return {'error': 'Cannot analyze zero-size input'}
    
    compression_ratio = compressed_size / original_size
    space_savings = (1 - compression_ratio) * 100
    bits_per_base = (compressed_size * 8) / dna_length if dna_length > 0 else 0
    
    # Theoretical Shannon limit for DNA storage (2 bits per base)
    shannon_efficiency = (2.0 / bits_per_base) * 100 if bits_per_base > 0 else 0
    
    return {
        'compression_ratio': compression_ratio,
        'space_savings_percent': space_savings,
        'bits_per_base': bits_per_base,
        'shannon_efficiency_percent': min(shannon_efficiency, 100),
        'theoretical_optimal': bits_per_base <= 2.0
    }


def create_compression_report(original_file: str, compressed_file: str, 
                            stats: Dict, output_path: Optional[str] = None) -> str:
    """
    Create a detailed compression report.
    
    Args:
        original_file: Path to original file
        compressed_file: Path to compressed file
        stats: Compression statistics dictionary
        output_path: Optional path to save report
        
    Returns:
        Report as formatted string
    """
    original_hash = calculate_file_hash(original_file)
    
    report_lines = [
        "=== Circular Chromosome Compression Report ===",
        f"Original file: {original_file}",
        f"Compressed file: {compressed_file}",
        f"Original hash (SHA256): {original_hash}",
        "",
        "=== Compression Statistics ===",
        f"Original size: {stats.get('original_size_bytes', 0):,} bytes",
        f"Compressed size: {stats.get('compressed_size_bytes', 0):,} bytes",
        f"Compression ratio: {stats.get('compression_ratio', 0):.4f}",
        f"Space savings: {stats.get('space_savings_percent', 0):.2f}%",
        f"Bits per base: {stats.get('bits_per_base', 0):.4f}",
        "",
        "=== Efficiency Analysis ===",
        f"Shannon efficiency: {stats.get('shannon_efficiency_percent', 0):.2f}%",
        f"Theoretical optimal: {stats.get('theoretical_optimal', False)}",
        "",
        "=== Algorithm Details ===",
        "Method: Circular Chromosome Compression (CCC)",
        "Inspired by: Dinoflagellate circular chromosomes",
        "Features: DVNP-like compression, trans-splicing markers",
        "Target: 1.5-2 bits/base for DNA storage optimization"
    ]
    
    report = "\n".join(report_lines)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
    
    return report


def verify_decompression_integrity(original_data: bytes, decompressed_data: bytes) -> bool:
    """
    Verify that decompressed data matches the original.
    
    Args:
        original_data: Original binary data
        decompressed_data: Decompressed binary data
        
    Returns:
        True if data matches, False otherwise
    """
    return original_data == decompressed_data


def estimate_dna_synthesis_cost(sequence_length: int, cost_per_base: float = 0.10) -> Dict[str, float]:
    """
    Estimate DNA synthesis cost based on sequence length.
    
    Args:
        sequence_length: Length of DNA sequence
        cost_per_base: Cost per nucleotide base in USD
        
    Returns:
        Dictionary with cost estimates
    """
    total_cost = sequence_length * cost_per_base
    
    # Add overhead costs (synthesis setup, purification, etc.)
    setup_cost = 50.0  # Base setup cost in USD
    purification_cost = total_cost * 0.2  # 20% of synthesis cost
    
    final_cost = total_cost + setup_cost + purification_cost
    
    return {
        'synthesis_cost_usd': total_cost,
        'setup_cost_usd': setup_cost,
        'purification_cost_usd': purification_cost,
        'total_cost_usd': final_cost,
        'cost_per_kb_data': final_cost / (sequence_length / 1000) if sequence_length > 0 else 0
    }


def benchmark_compression_speed(compressor, test_data_sizes: List[int]) -> Dict[int, Dict[str, float]]:
    """
    Benchmark compression speed with different data sizes.
    
    Args:
        compressor: CircularChromosomeCompressor instance
        test_data_sizes: List of test data sizes in bytes
        
    Returns:
        Dictionary mapping data size to performance metrics
    """
    import time
    
    results = {}
    
    for size in test_data_sizes:
        # Generate test data
        test_data = bytes(range(256)) * (size // 256) + bytes(range(size % 256))
        
        # Benchmark compression
        start_time = time.time()
        compressed_data, metadata = compressor.compress(test_data)
        compression_time = time.time() - start_time
        
        # Benchmark decompression
        start_time = time.time()
        decompressed_data = compressor.decompress(compressed_data, metadata)
        decompression_time = time.time() - start_time
        
        # Calculate throughput
        compression_throughput = size / compression_time if compression_time > 0 else 0
        decompression_throughput = size / decompression_time if decompression_time > 0 else 0
        
        results[size] = {
            'compression_time_sec': compression_time,
            'decompression_time_sec': decompression_time,
            'compression_throughput_bytes_sec': compression_throughput,
            'decompression_throughput_bytes_sec': decompression_throughput,
            'total_time_sec': compression_time + decompression_time,
            'integrity_verified': verify_decompression_integrity(test_data, decompressed_data)
        }
    
    return results
