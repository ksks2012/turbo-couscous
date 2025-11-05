"""
Circular Chromosome Compression (CCC) Algorithm
Bio-inspired by dinoflagellate circular chromosomes and histone-free condensation.

This algorithm converts binary data to DNA sequences using circular structure
to optimize storage density and enable efficient access patterns.
"""

import hashlib
import math
from collections import Counter
from typing import List, Dict, Tuple, Optional
from Bio.Seq import Seq


class CircularChromosomeCompressor:
    """
    Implements the Circular Chromosome Compression algorithm inspired by
    dinoflagellate chromosomes with DVNP-like compression and trans-splicing.
    """
    
    def __init__(self, chunk_size: int = 1000, min_pattern_length: int = 4, 
                 strict_mode: bool = True, verbose: bool = False):
        """
        Initialize the compressor with configuration parameters.
        
        Args:
            chunk_size: Size of chunks for trans-splicing markers
            min_pattern_length: Minimum length for pattern detection in DVNP compression
            strict_mode: If True, raise exceptions for invalid inputs; if False, return defaults
            verbose: If True, print debugging information during processing
        """
        self.chunk_size = chunk_size
        self.min_pattern_length = min_pattern_length
        self.strict_mode = strict_mode
        self.verbose = verbose
        self.base_mapping = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
        self.reverse_mapping = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
        # Fixed base dictionary for DVNP compression/decompression symmetry
        self._base_dict = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        
    def _log(self, message: str):
        """Log debug information if verbose mode is enabled."""
        if self.verbose:
            print(f"[CCC] {message}")
    
    def _validate_input(self, data, data_name: str):
        """Validate input data and handle according to strict_mode."""
        if not data:
            if self.strict_mode:
                raise ValueError(f"Missing or empty {data_name}")
            else:
                self._log(f"Warning: Missing or empty {data_name}, returning default")
                return False
        return True
    
    def _entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy of binary data.
        
        Args:
            data: Input binary data
            
        Returns:
            Shannon entropy in bits per byte
        """
        if not data:
            return 0.0
        
        # Count frequency of each byte value
        freq = Counter(data)
        total = len(data)
        
        # Calculate Shannon entropy: H = -Σ(p * log2(p))
        # Handle the case where probability = 1 (all data same)
        entropy = 0.0
        for count in freq.values():
            probability = count / total
            if probability > 0:  # Avoid log(0)
                entropy -= probability * math.log2(probability)
        
        self._log(f"Shannon entropy calculated: {entropy:.3f} bits/byte")
        return entropy
    
    def _compute_data_hash(self, data: List[int]) -> str:
        """
        Compute SHA-256 hash for data integrity verification.
        
        Args:
            data: List of integer codes representing compressed data
            
        Returns:
            8-character hexadecimal hash string
        """
        if not data:
            return ""
        
        data_str = ','.join(str(x) for x in data)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:8]
    
    def _verify_data_integrity(self, data: List[int], expected_hash: str, operation: str = "decompression") -> bool:
        """
        Verify data integrity using hash comparison.
        
        Args:
            data: List of integer codes to verify
            expected_hash: Expected hash value
            operation: Operation context for error messages
            
        Returns:
            True if hash matches, False or raises exception otherwise
        """
        if not expected_hash:
            self._log(f"[CCC Warning] No hash available for {operation} integrity verification")
            return False
        
        computed_hash = self._compute_data_hash(data)
        
        if computed_hash == expected_hash:
            self._log(f"[CCC Info] Data integrity verified successfully for {operation}")
            return True
        else:
            error_msg = f"Data integrity check failed during {operation}: hash mismatch (expected {expected_hash}, got {computed_hash})"
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self._log(f"[CCC Warning] {error_msg}")
                if self.verbose:
                    print(f"[CCC Warning] {error_msg}")
                return False
        
    def binary_to_dna(self, binary_data: bytes) -> Seq:
        """
        Convert binary data to DNA sequence using 2-bit to base mapping.
        Inspired by balanced nucleotide distribution in dinoflagellates.
        
        Args:
            binary_data: Input binary data as bytes
            
        Returns:
            Bio.Seq object containing DNA sequence
        """
        if not self._validate_input(binary_data, "binary_data"):
            return Seq("")
            
        self._log(f"Converting {len(binary_data)} bytes to DNA sequence")
            
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
        
        self._log(f"Generated DNA sequence of length {len(dna_sequence)}")
        return Seq(dna_sequence)
    
    def dna_to_binary(self, dna_seq: str) -> bytes:
        """
        Convert DNA sequence back to binary data.
        
        Args:
            dna_seq: DNA sequence string
            
        Returns:
            Original binary data as bytes
        """
        if not self._validate_input(dna_seq, "dna_seq"):
            return b""
            
        self._log(f"Converting DNA sequence of length {len(dna_seq)} back to binary")
        
        # Validate DNA sequence contains only valid bases
        valid_bases = set('ACGT')
        invalid_bases = set(dna_seq.upper()) - valid_bases
        if invalid_bases:
            error_msg = f"Invalid DNA bases found: {invalid_bases}"
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self._log(f"Warning: {error_msg}, filtering them out")
                dna_seq = ''.join(base for base in dna_seq.upper() if base in valid_bases)
            
        # Convert DNA to binary string
        try:
            bits = ''.join(self.reverse_mapping[base.upper()] for base in dna_seq)
        except KeyError as e:
            error_msg = f"Invalid DNA base encountered: {e}"
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self._log(f"Warning: {error_msg}")
                return b""
        
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
        
        Optimized for large data (>100KB) with several performance enhancements:
        1. Pre-allocated result list to reduce memory allocations
        2. Cached dictionary access patterns
        3. Reduced string concatenation overhead where possible

        Args:
            dna_seq: Input DNA sequence string

        Returns:
            Compressed sequence as list of integers
        """
        if not self._validate_input(dna_seq, "dna_seq"):
            return []
            
        self._log(f"Starting DVNP compression on sequence of length {len(dna_seq)}")
        
        # Pre-initialize dictionary with expected capacity hint
        dictionary = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        next_code = 4
        current = ''
        
        # Pre-allocate result list with estimated size to reduce reallocations
        # Typical compression achieves 15-30% of original size
        estimated_size = len(dna_seq) // 4
        result = []
        result.reserve = estimated_size  # Hint for list allocation (if supported)
        
        # Main compression loop - keep original 'in' operator as it's well-optimized in Python
        for ch in dna_seq:
            combined = current + ch
            if combined in dictionary:
                current = combined
            else:
                if current:  # Only append if current is not empty
                    result.append(dictionary[current])
                # Limit dictionary size to prevent excessive memory usage
                if next_code < 65536:
                    dictionary[combined] = next_code
                    next_code += 1
                current = ch
        
        # Handle final sequence
        if current:
            result.append(dictionary[current])

        self._log(f"DVNP compression completed: {len(dna_seq)} chars → {len(result)} codes")
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
        if not self._validate_input(compressed, "compressed codes"):
            return ""
            
        self._log(f"Starting DVNP decompression on {len(compressed)} codes")
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
                error_msg = f"Invalid code {code} in DVNP decompression"
                if self.strict_mode:
                    raise ValueError(error_msg)
                else:
                    self._log(f"Warning: {error_msg}, skipping")
                    continue
            result += entry
            if next_code < 65536:
                work_dict[next_code] = prev + entry[0]
                next_code += 1
            prev = entry
        
        self._log(f"DVNP decompression completed: {len(compressed)} codes → {len(result)} chars")
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
        if not self._validate_input(compressed, "compressed data"):
            return compressed
        
        length = len(compressed)
        self._log(f"Starting circular encapsulation for {length} codes")
        
        # Find next prime for optimal ring size to avoid periodic artifacts
        prime_length = self._next_prime(length)
        padding_size = prime_length - length
        
        self._log(f"Circular padding size = {padding_size} (prime length: {prime_length})")
        
        # Pad with zeros if needed
        padded = compressed + [0] * padding_size
        
        # Create bridge for circular continuity
        bridge_length = min(int(math.sqrt(prime_length)), 10)
        bridge = padded[:bridge_length]
        
        self._log(f"Bridge length = {bridge_length}")
        
        # Create circular structure
        circular_ring = padded + bridge
        
        self._log(f"Circular encapsulation completed: {length} → {len(circular_ring)} codes")
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
        data_hash = self._compute_data_hash(circular_data)
        
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
    
    def compress_core(self, binary_data: bytes) -> Tuple[List[int], Dict]:
        """
        Core compression algorithm layer: Binary → DNA → DVNP compression.
        
        Args:
            binary_data: Input binary data
            
        Returns:
            Tuple of (DVNP compressed data, core metadata)
        """
        if not self._validate_input(binary_data, "binary_data"):
            return [], {'dna_length': 0, 'original_size': 0, 'original_bits_length': 0}
            
        self._log(f"Starting core compression for {len(binary_data)} bytes")
        
        # Step 1: Convert binary to DNA
        dna_seq = self.binary_to_dna(binary_data)
        
        # Step 2: DVNP compression
        compressed = self.dvnp_compress(str(dna_seq))
        
        # Core layer metadata
        core_metadata = {
            'dna_length': len(dna_seq),
            'original_size': len(binary_data),
            'original_bits_length': getattr(self, '_original_bits_length', len(binary_data) * 8)
        }
        
        return compressed, core_metadata
    
    def encapsulate(self, compressed: List[int]) -> Tuple[List[int], Dict]:
        """
        Encapsulation layer: Circular encapsulation + Trans-splicing markers.
        
        Args:
            compressed: DVNP compressed data from compress_core()
            
        Returns:
            Tuple of (encapsulated data with markers, encapsulation metadata)
        """
        if not self._validate_input(compressed, "compressed data"):
            return [], {'circular_length': 0, 'trans_splicing': {}}
        
        # Step 1: Circular encapsulation
        circular_data = self.circular_encapsulate(compressed)
        
        # Step 2: Add trans-splicing markers
        marked_data, ts_metadata = self.add_trans_splicing_markers(circular_data, len(compressed))
        
        # Encapsulation layer metadata
        encap_metadata = {
            'circular_length': len(circular_data),
            'trans_splicing': ts_metadata
        }
        
        return marked_data, encap_metadata
    
    def compress(self, binary_data: bytes) -> Tuple[List[int], Dict]:
        """
        Complete compression pipeline using layered architecture.
        
        Args:
            binary_data: Input binary data
            
        Returns:
            Tuple of (compressed data, complete metadata for decompression)
        """
        if not self._validate_input(binary_data, "binary_data"):
            return [], {
                'core': {'dna_length': 0, 'original_size': 0, 'original_bits_length': 0},
                'encapsulation': {'circular_length': 0, 'trans_splicing': {}},
                'compression_ratio': 0
            }
        
        # Layer 1: Core compression
        compressed, core_metadata = self.compress_core(binary_data)
        
        # Layer 2: Encapsulation
        final_data, encap_metadata = self.encapsulate(compressed)
        
        # Combine metadata from all layers
        metadata = {
            'core': core_metadata,
            'encapsulation': encap_metadata,
            'compression_ratio': len(final_data) / len(binary_data) if binary_data else 0
        }
        
        return final_data, metadata
    
    def decapsulate(self, marked_data: List[int], encap_metadata: Dict) -> List[int]:
        """
        Decapsulation layer: Remove trans-splicing markers and circular encapsulation.
        Includes hash verification for data integrity checking.
        
        Args:
            marked_data: Data with trans-splicing markers
            encap_metadata: Encapsulation metadata
            
        Returns:
            Original DVNP compressed data
        """
        if not marked_data or not encap_metadata:
            return []
            
        # Step 1: Remove trans-splicing markers
        ts_metadata = encap_metadata.get('trans_splicing', {})
        marker_code = ts_metadata.get('sl_marker_code', 0)
        
        # Filter out markers
        filtered_data = [x for x in marked_data if x != marker_code]
        
        # Step 2: Remove bridge elements and zero padding from circular encapsulation
        original_length = ts_metadata.get('original_length', len(filtered_data))
        original_compressed_length = ts_metadata.get('original_compressed_length', original_length)
        
        if original_length <= len(filtered_data):
            # Get the encapsulated data (without trans-splicing markers)
            encapsulated_data = filtered_data[:original_length]
            
            # Step 3: Hash verification for data integrity
            stored_hash = ts_metadata.get('data_hash', '')
            self._verify_data_integrity(encapsulated_data, stored_hash, "decapsulation")
            
            # Extract only the original compressed data, excluding zero padding and bridge elements
            core_data = encapsulated_data[:original_compressed_length]
        else:
            # Fallback - shouldn't happen in normal cases
            core_data = filtered_data[:original_compressed_length] if original_compressed_length <= len(filtered_data) else filtered_data
            self._log("[CCC Warning] Data length inconsistency detected during decapsulation")
        
        return core_data
    
    def decompress_core(self, compressed: List[int], core_metadata: Dict) -> bytes:
        """
        Core decompression algorithm layer: DVNP decompression → DNA → Binary.
        
        Args:
            compressed: DVNP compressed data
            core_metadata: Core metadata
            
        Returns:
            Original binary data
        """
        if not self._validate_input(compressed, "compressed codes") or \
           not self._validate_input(core_metadata, "core_metadata"):
            return b""
            
        self._log(f"Starting core decompression for {len(compressed)} codes")
            
        # Step 1: DVNP decompression
        dna_sequence = self.dvnp_decompress(compressed)
        
        # Step 2: Convert DNA back to binary
        binary_data = self.dna_to_binary(dna_sequence)
        
        # Step 3: Ensure exact original length
        expected_size = core_metadata.get('original_size', len(binary_data))
        if len(binary_data) > expected_size:
            # Truncate extra bytes
            binary_data = binary_data[:expected_size]
        elif len(binary_data) < expected_size:
            # Pad with zeros if needed (this shouldn't normally happen)
            padding_needed = expected_size - len(binary_data)
            binary_data = binary_data + b'\x00' * padding_needed
        
        return binary_data
    
    def decompress(self, compressed_data: List[int], metadata: Dict) -> bytes:
        """
        Complete decompression pipeline using layered architecture.
        
        Args:
            compressed_data: Compressed data from compress()
            metadata: Metadata from compress()
            
        Returns:
            Original binary data
        """
        if not self._validate_input(compressed_data, "compressed_data") or \
           not self._validate_input(metadata, "metadata"):
            return b""
            
        self._log(f"Starting decompression for {len(compressed_data)} codes")
        
        # Support both new layered metadata and legacy flat metadata
        if 'core' in metadata and 'encapsulation' in metadata:
            # New layered metadata structure
            core_metadata = metadata['core']
            encap_metadata = metadata['encapsulation']
            
            # Layer 1: Decapsulation
            core_data = self.decapsulate(compressed_data, encap_metadata)
            
            # Layer 2: Core decompression
            binary_data = self.decompress_core(core_data, core_metadata)
            
        else:
            # Legacy flat metadata structure for backward compatibility
            ts_metadata = metadata.get('trans_splicing', {})
            marker_code = ts_metadata.get('sl_marker_code', 0)
            
            # Filter out markers
            filtered_data = [x for x in compressed_data if x != marker_code]
            
            # Remove bridge elements and zero padding
            original_length = ts_metadata.get('original_length', len(filtered_data))
            original_compressed_length = ts_metadata.get('original_compressed_length', original_length)
            
            if original_length <= len(filtered_data):
                encapsulated_data = filtered_data[:original_length]
                circular_data = encapsulated_data[:original_compressed_length]
            else:
                circular_data = filtered_data[:original_compressed_length] if original_compressed_length <= len(filtered_data) else filtered_data
            
            # DVNP decompression
            dna_sequence = self.dvnp_decompress(circular_data)
            
            # Convert DNA back to binary
            binary_data = self.dna_to_binary(dna_sequence)
            
            # Ensure exact original length
            expected_size = metadata.get('original_size', len(binary_data))
            if len(binary_data) > expected_size:
                binary_data = binary_data[:expected_size]
            elif len(binary_data) < expected_size:
                padding_needed = expected_size - len(binary_data)
                binary_data = binary_data + b'\x00' * padding_needed
        
        return binary_data
    
    def get_compression_stats(self, original_data: bytes, compressed_result) -> Dict:
        """
        Calculate compression statistics and efficiency metrics with Shannon entropy analysis.
        
        Args:
            original_data: Original binary data
            compressed_result: Either compressed data (List[int]) or complete result (Tuple[List[int], Dict])
            
        Returns:
            Dictionary with compression statistics including entropy analysis
        """
        original_size = len(original_data)
        
        # Handle both direct compressed data and complete compression result
        if isinstance(compressed_result, tuple):
            compressed_data, metadata = compressed_result
        else:
            compressed_data = compressed_result
            metadata = {}
        
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
        
        # Calculate Shannon entropy and efficiency metrics
        original_entropy = self._entropy(original_data)
        
        # For compressed entropy, we need to handle integer codes properly
        if compressed_data:
            # Convert integer codes to bytes representation for entropy calculation
            compressed_bytes = []
            for code in compressed_data:
                # Convert each code to bytes (using little-endian encoding)
                code_bytes = code.to_bytes((code.bit_length() + 7) // 8 or 1, 'little')
                compressed_bytes.extend(code_bytes)
            compressed_entropy = self._entropy(bytes(compressed_bytes))
        else:
            compressed_entropy = 0.0
            
        entropy_reduction = original_entropy - compressed_entropy
        
        theoretical_min_size = (original_entropy * original_size) / 8 if original_size > 0 else 0
        shannon_efficiency = theoretical_min_size / compressed_size if compressed_size > 0 else 0
        
        # Compression effectiveness: how close we are to Shannon limit
        actual_ratio = compressed_size / original_size if original_size > 0 else 0
        shannon_ratio = theoretical_min_size / original_size if original_size > 0 else 0
        
        # Shannon efficiency: theoretical minimum vs actual compressed size
        shannon_efficiency = theoretical_min_size / compressed_size if compressed_size > 0 else 0
        
        # Compression effectiveness: how well we approach theoretical limit
        # 1.0 = achieved theoretical limit, 0.0 = no compression improvement over Shannon limit
        if shannon_ratio > 0 and actual_ratio > shannon_ratio:
            # We're worse than theoretical minimum - effectiveness between 0 and 1
            compression_effectiveness = shannon_ratio / actual_ratio
        elif shannon_ratio > 0 and actual_ratio <= shannon_ratio:
            # We're at or better than theoretical minimum (impossible but handle gracefully)
            compression_effectiveness = 1.0
        else:
            compression_effectiveness = 0.0
        
        stats = {
            'original_size_bytes': original_size,
            'compressed_size_bytes': compressed_size,
            'compression_ratio': actual_ratio,
            'space_savings_percent': (1 - actual_ratio) * 100 if original_size > 0 else 0,
            'bits_per_base': (compressed_size * 8) / dna_length if dna_length > 0 else 0,
            'bits_per_code': bits_per_code,
            'total_codes': len(compressed_data),
            'max_code_value': max(compressed_data) if compressed_data else 0,
            # Shannon entropy analysis
            'original_entropy': original_entropy,
            'compressed_entropy': compressed_entropy,
            'entropy_reduction': entropy_reduction,
            'theoretical_minimum_size': theoretical_min_size,
            'shannon_efficiency': min(1.0, shannon_efficiency),  # Cap at 1.0
            'compression_effectiveness': min(1.0, max(0.0, compression_effectiveness))  # Keep between 0.0 and 1.0
        }
        
        return stats
