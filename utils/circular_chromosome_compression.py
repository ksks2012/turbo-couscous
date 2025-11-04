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
        # Fixed base dictionary for DVNP compression/decompression symmetry
        self._base_dict = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        
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
        
        # Convert binary string to bytes
        byte_array = []
        for i in range(0, len(bits), 8):
            byte_chunk = bits[i:i+8]
            if len(byte_chunk) == 8:
                byte_array.append(int(byte_chunk, 2))
            elif len(byte_chunk) > 0:
                # Handle incomplete byte by padding with zeros
                padded_chunk = byte_chunk.ljust(8, '0')
                byte_array.append(int(padded_chunk, 2))
                
        return bytes(byte_array)
        
    def dvnp_compress(self, dna_seq: str) -> List[int]:
        """
        DVNP-simulated compression using improved LZW-like algorithm to remove repetitive patterns.
        Inspired by dinoflagellate viral nucleoprotein condensation mechanisms.

        Args:
            dna_seq: Input DNA sequence string

        Returns:
            Compressed sequence as list of integers
        """
        if not dna_seq:
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
                result.append(dictionary[current])
                if next_code < 65536:
                    dictionary[combined] = next_code
                    next_code += 1
                current = ch
        if current:
            result.append(dictionary[current])

        return result

    def dvnp_decompress(self, compressed: List[int]) -> str:
        """
        Decompress the DVNP-compressed sequence using improved LZW decompression.
        Must match compression logic exactly for perfect reconstruction.
        Uses the fixed base dictionary for symmetry with compression.
        
        Args:
            compressed: List of integer codes
            
        Returns:
            Decompressed DNA sequence string
        """
        if not compressed:
            return ""
        work_dict = self._base_dict.copy()
        next_code = 4
        prev = work_dict[compressed[0]]
        result = prev
        for code in compressed[1:]:
            if code in work_dict:
                entry = work_dict[code]
            elif code == next_code:
                entry = prev + prev[0]
            else:
                raise ValueError(f"Invalid code {code}")
            result += entry
            if next_code < 65536:
                work_dict[next_code] = prev + entry[0]
                next_code += 1
            prev = entry
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
    
    def add_trans_splicing_markers(self, circular_data: List[int], original_compressed_length: int = None) -> Tuple[List, Dict]:
        """
        Add trans-splicing markers for error correction and decoding guidance.
        Inspired by dinoflagellate trans-splicing mechanisms.
        
        Args:
            circular_data: Circular compressed data
            original_compressed_length: Length of original compressed data before circular encapsulation
            
        Returns:
            Tuple of (marked data, metadata for decoding)
        """
        if not circular_data:
            return [], {'sl_marker_code': 0, 'chunk_size': self.chunk_size, 'original_length': 0, 'marker_positions': [], 'data_hash': '', 'original_compressed_length': 0}
            
        # Generate spliced leader marker that doesn't conflict with data
        data_str = ','.join(str(x) for x in circular_data)
        data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:8]
        
        # Find a marker code that doesn't exist in the data
        max_value = max(circular_data) if circular_data else 0
        data_set = set(circular_data)
        
        # Start with a value guaranteed to be outside the data range
        sl_marker_code = max_value + 1
        
        # Double-check it doesn't conflict (though it shouldn't)
        while sl_marker_code in data_set:
            sl_marker_code += 1
        
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
            'data_hash': data_hash,
            'original_compressed_length': original_compressed_length if original_compressed_length is not None else len(circular_data)
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
            return [], {'trans_splicing': {}, 'original_size': 0, 'dna_length': 0, 'compression_ratio': 0, 'original_bits_length': 0}
        
        # Step 1: Convert binary to DNA
        dna_seq = self.binary_to_dna(binary_data)
        
        # Step 2: DVNP compression
        compressed = self.dvnp_compress(str(dna_seq))
        
        # Step 3: Circular encapsulation
        circular_data = self.circular_encapsulate(compressed)
        
        # Step 4: Add trans-splicing markers with original compressed length
        final_data, ts_metadata = self.add_trans_splicing_markers(circular_data, len(compressed))
        
        # Combine all metadata (no need to store dvnp_dictionary anymore)
        metadata = {
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
        
        # Remove bridge elements and zero padding from circular encapsulation
        original_length = ts_metadata.get('original_length', len(filtered_data))
        original_compressed_length = ts_metadata.get('original_compressed_length', original_length)
        
        if original_length <= len(filtered_data):
            # Get the encapsulated data (without trans-splicing markers)
            encapsulated_data = filtered_data[:original_length]
            
            # Extract only the original compressed data, excluding zero padding and bridge elements
            circular_data = encapsulated_data[:original_compressed_length]
        else:
            # Fallback - shouldn't happen in normal cases
            circular_data = filtered_data[:original_compressed_length] if original_compressed_length <= len(filtered_data) else filtered_data
        
        # Step 2: DVNP decompression
        dna_sequence = self.dvnp_decompress(circular_data)
        
        # Step 3: Convert DNA back to binary
        binary_data = self.dna_to_binary(dna_sequence)
        
        # Ensure exact original length
        if 'original_size' in metadata:
            expected_size = metadata['original_size']
            if len(binary_data) > expected_size:
                # Truncate extra bytes
                binary_data = binary_data[:expected_size]
            elif len(binary_data) < expected_size:
                # Pad with zeros if needed (this shouldn't normally happen)
                padding_needed = expected_size - len(binary_data)
                binary_data = binary_data + b'\x00' * padding_needed
        
        
        return binary_data
    
    def get_compression_stats(self, original_data: bytes, compressed_data: List[int]) -> Dict:
        """
        Calculate compression statistics and efficiency metrics with accurate bit counting.
        
        Args:
            original_data: Original binary data
            compressed_data: Compressed data
            
        Returns:
            Dictionary with compression statistics
        """
        original_size = len(original_data)
        
        # More accurate size calculation: determine bits needed per code
        if compressed_data:
            max_code = max(compressed_data) if compressed_data else 0
            bits_per_code = max(16, (max_code.bit_length() + 7) // 8 * 8)  # Round up to byte boundary, min 16-bit
            compressed_size_bits = len(compressed_data) * bits_per_code
            compressed_size = compressed_size_bits // 8
        else:
            compressed_size = 0
            bits_per_code = 16
        
        # Calculate DNA sequence length for bits per base calculation
        dna_length = original_size * 4  # 2 bits per base -> 4 bases per byte
        
        stats = {
            'original_size_bytes': original_size,
            'compressed_size_bytes': compressed_size,
            'compression_ratio': compressed_size / original_size if original_size > 0 else 0,
            'space_savings_percent': (1 - compressed_size / original_size) * 100 if original_size > 0 else 0,
            'bits_per_base': (compressed_size * 8) / dna_length if dna_length > 0 else 0,
            'bits_per_code': bits_per_code,
            'total_codes': len(compressed_data),
            'max_code_value': max(compressed_data) if compressed_data else 0
        }
        
        return stats
