"""
Circular Chromosome Compression (CCC) Algorithm
Bio-inspired by dinoflagellate circular chromosomes and histone-free condensation.

This algorithm converts binary data to DNA sequences using circular structure
to optimize storage density and enable efficient access patterns.
"""

import hashlib
import math
from typing import List, Dict, Tuple, Optional
from Bio.Seq import Seq


class CircularChromosomeCompressor:
    """
    Implements the Circular Chromosome Compression algorithm inspired by
    dinoflagellate chromosomes with DVNP-like compression and trans-splicing.
    """
    
    def __init__(self, chunk_size: int = 1000, min_pattern_length: int = 4):
        """
        Initialize the compressor with configuration parameters.
        
        Args:
            chunk_size: Size of chunks for trans-splicing markers
            min_pattern_length: Minimum length for pattern detection in DVNP compression
        """
        self.chunk_size = chunk_size
        self.min_pattern_length = min_pattern_length
        self.base_mapping = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
        self.reverse_mapping = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        
    def binary_to_dna(self, binary_data: bytes) -> Seq:
        """
        Convert binary data to DNA sequence using 2-bit to base mapping.
        Inspired by balanced nucleotide distribution in dinoflagellates.
        
        Args:
            binary_data: Input binary data as bytes
            
        Returns:
            Bio.Seq object containing DNA sequence
        """
        if not binary_data:
            return Seq("")
            
        # Convert bytes to binary string
        bits = ''.join(f'{byte:08b}' for byte in binary_data)
        
        # Store original length for proper reconstruction
        self._original_bits_length = len(bits)
        
        # Pad if length is not even
        if len(bits) % 2 != 0:
            bits += '0'
            
        # Convert to DNA sequence
        dna_sequence = ''.join(
            self.base_mapping[bits[i:i+2]] 
            for i in range(0, len(bits), 2)
        )
        
        return Seq(dna_sequence)
    
    def dna_to_binary(self, dna_seq: str) -> bytes:
        """
        Convert DNA sequence back to binary data.
        
        Args:
            dna_seq: DNA sequence string
            
        Returns:
            Original binary data as bytes
        """
        if not dna_seq:
            return b""
            
        # Convert DNA to binary string
        bits = ''.join(self.reverse_mapping[base] for base in dna_seq)
        
        # Use original length if available to avoid padding issues
        if hasattr(self, '_original_bits_length'):
            bits = bits[:self._original_bits_length]
        
        # Convert binary string to bytes
        byte_array = []
        for i in range(0, len(bits), 8):
            byte_chunk = bits[i:i+8]
            if len(byte_chunk) == 8:  # Only process complete bytes
                byte_array.append(int(byte_chunk, 2))
                
        return bytes(byte_array)
    
    def dvnp_compress(self, dna_seq: str) -> Tuple[List[int], Dict[int, str]]:
        """
        DVNP-simulated compression using LZW-like algorithm to remove repetitive patterns.
        Inspired by dinoflagellate viral nucleoprotein condensation mechanisms.
        
        Args:
            dna_seq: Input DNA sequence string
            
        Returns:
            Tuple of (compressed sequence as integers, dictionary for decompression)
        """
        # Initialize dictionary with single bases
        dictionary = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        next_code = 4
        
        compressed = []
        current_pattern = ""
        
        for base in dna_seq:
            new_pattern = current_pattern + base
            
            if new_pattern in dictionary:
                current_pattern = new_pattern
            else:
                # Output the code for current pattern
                if current_pattern:
                    compressed.append(dictionary[current_pattern])
                
                # Add new pattern to dictionary if it meets minimum length
                if len(new_pattern) >= self.min_pattern_length:
                    dictionary[new_pattern] = next_code
                    next_code += 1
                
                current_pattern = base
        
        # Output the final pattern
        if current_pattern:
            compressed.append(dictionary[current_pattern])
        
        # Create reverse dictionary for decompression
        reverse_dict = {v: k for k, v in dictionary.items()}
        
        return compressed, reverse_dict
    
    def dvnp_decompress(self, compressed: List[int], dictionary: Dict[int, str]) -> str:
        """
        Decompress the DVNP-compressed sequence.
        
        Args:
            compressed: List of integer codes
            dictionary: Decompression dictionary
            
        Returns:
            Decompressed DNA sequence string
        """
        if not compressed:
            return ""
        
        # Initialize with first code
        result = dictionary[compressed[0]]
        current_pattern = result
        
        for i in range(1, len(compressed)):
            code = compressed[i]
            
            if code in dictionary:
                new_pattern = dictionary[code]
            else:
                # Handle case where code is not in dictionary yet
                new_pattern = current_pattern + current_pattern[0]
            
            result += new_pattern
            
            # Add new pattern to dictionary
            if len(current_pattern + new_pattern[0]) >= self.min_pattern_length:
                next_code = max(dictionary.keys()) + 1
                dictionary[next_code] = current_pattern + new_pattern[0]
            
            current_pattern = new_pattern
        
        return result
    
    def _next_prime(self, n: int) -> int:
        """Find the next prime number greater than or equal to n."""
        if n < 2:
            return 2
        
        while not self._is_prime(n):
            n += 1
        return n
    
    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def circular_encapsulate(self, compressed: List[int]) -> List[int]:
        """
        Encapsulate compressed data in circular structure to eliminate boundary waste.
        Inspired by dinoflagellate circular chromosomes.
        
        Args:
            compressed: Compressed sequence as list of integers
            
        Returns:
            Circular-ready sequence with bridge elements
        """
        if not compressed:
            return compressed
        
        length = len(compressed)
        
        # Find next prime for optimal ring size to avoid periodic artifacts
        prime_length = self._next_prime(length)
        
        # Pad with zeros if needed
        padded = compressed + [0] * (prime_length - length)
        
        # Create bridge for circular continuity
        bridge_length = min(int(math.sqrt(prime_length)), 10)
        bridge = padded[:bridge_length]
        
        # Create circular structure
        circular_ring = padded + bridge
        
        return circular_ring
    
    def add_trans_splicing_markers(self, circular_data: List[int]) -> Tuple[List, Dict]:
        """
        Add trans-splicing markers for error correction and decoding guidance.
        Inspired by dinoflagellate trans-splicing mechanisms.
        
        Args:
            circular_data: Circular compressed data
            
        Returns:
            Tuple of (marked data, metadata for decoding)
        """
        if not circular_data:
            return [], {'sl_marker_code': 0, 'chunk_size': self.chunk_size, 'original_length': 0, 'marker_positions': [], 'data_hash': ''}
            
        # Generate spliced leader marker - ensure values are in byte range
        safe_data = [x % 256 for x in circular_data]  # Ensure all values are in 0-255 range
        data_hash = hashlib.sha256(bytes(safe_data)).hexdigest()[:8]
        sl_marker_code = hash(f"SL_MARKER_{data_hash}") % 65536  # 16-bit marker
        
        marked_data = []
        marker_positions = []
        
        # Insert markers at regular intervals
        for i in range(0, len(circular_data), self.chunk_size):
            chunk = circular_data[i:i+self.chunk_size]
            
            # Add marker before chunk
            marked_data.append(sl_marker_code)
            marker_positions.append(len(marked_data) - 1)
            
            # Add chunk data
            marked_data.extend(chunk)
        
        # Metadata for decoding
        metadata = {
            'sl_marker_code': sl_marker_code,
            'chunk_size': self.chunk_size,
            'original_length': len(circular_data),
            'marker_positions': marker_positions,
            'data_hash': data_hash
        }
        
        return marked_data, metadata
    
    def compress(self, binary_data: bytes) -> Tuple[List[int], Dict]:
        """
        Complete compression pipeline using circular chromosome approach.
        
        Args:
            binary_data: Input binary data
            
        Returns:
            Tuple of (compressed data, metadata for decompression)
        """
        if not binary_data:
            return [], {'dvnp_dictionary': {}, 'trans_splicing': {}, 'original_size': 0, 'dna_length': 0, 'compression_ratio': 0, 'original_bits_length': 0}
        
        # Step 1: Convert binary to DNA
        dna_seq = self.binary_to_dna(binary_data)
        
        # Step 2: DVNP compression
        compressed, dvnp_dict = self.dvnp_compress(str(dna_seq))
        
        # Step 3: Circular encapsulation
        circular_data = self.circular_encapsulate(compressed)
        
        # Step 4: Add trans-splicing markers
        final_data, ts_metadata = self.add_trans_splicing_markers(circular_data)
        
        # Combine all metadata
        metadata = {
            'dvnp_dictionary': dvnp_dict,
            'trans_splicing': ts_metadata,
            'original_size': len(binary_data),
            'dna_length': len(dna_seq),
            'compression_ratio': len(final_data) / len(binary_data) if binary_data else 0,
            'original_bits_length': getattr(self, '_original_bits_length', len(binary_data) * 8)
        }
        
        return final_data, metadata
    
    def decompress(self, compressed_data: List[int], metadata: Dict) -> bytes:
        """
        Complete decompression pipeline.
        
        Args:
            compressed_data: Compressed data from compress()
            metadata: Metadata from compress()
            
        Returns:
            Original binary data
        """
        if not compressed_data or not metadata:
            return b""
            
        # Step 1: Remove trans-splicing markers
        ts_metadata = metadata.get('trans_splicing', {})
        marker_code = ts_metadata.get('sl_marker_code', 0)
        
        # Filter out markers
        filtered_data = [x for x in compressed_data if x != marker_code]
        
        # Remove bridge elements (circular padding)
        original_length = ts_metadata.get('original_length', len(filtered_data))
        circular_data = filtered_data[:original_length]
        
        # Step 2: DVNP decompression
        dvnp_dict = metadata.get('dvnp_dictionary', {})
        dna_sequence = self.dvnp_decompress(circular_data, dvnp_dict)
        
        # Step 3: Convert DNA back to binary
        # Restore original bits length to avoid padding issues
        if 'original_bits_length' in metadata:
            self._original_bits_length = metadata['original_bits_length']
            
        binary_data = self.dna_to_binary(dna_sequence)
        
        return binary_data
    
    def get_compression_stats(self, original_data: bytes, compressed_data: List[int]) -> Dict:
        """
        Calculate compression statistics and efficiency metrics.
        
        Args:
            original_data: Original binary data
            compressed_data: Compressed data
            
        Returns:
            Dictionary with compression statistics
        """
        original_size = len(original_data)
        compressed_size = len(compressed_data) * 2  # Assuming 2 bytes per int on average
        
        stats = {
            'original_size_bytes': original_size,
            'compressed_size_bytes': compressed_size,
            'compression_ratio': compressed_size / original_size if original_size > 0 else 0,
            'space_savings_percent': (1 - compressed_size / original_size) * 100 if original_size > 0 else 0,
            'bits_per_base': compressed_size * 8 / (original_size * 4) if original_size > 0 else 0  # DNA has 4 possible bases
        }
        
        return stats
