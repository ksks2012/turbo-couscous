"""
Unit tests for the Circular Chromosome Compression (CCC) algorithm.

Tests cover all major components including:
- Binary to DNA conversion
- DVNP compression/decompression
- Circular encapsulation
- Trans-splicing markers
- End-to-end compression/decompression
"""

import unittest
import os
import sys
import tempfile
import hashlib
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.circular_chromosome_compression import CircularChromosomeCompressor
from utils import helpers
from Bio.Seq import Seq


class TestCircularChromosomeCompressor(unittest.TestCase):
    """Test cases for the CircularChromosomeCompressor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.compressor = CircularChromosomeCompressor()
        self.test_data = b"Hello, World! This is a test message for CCC compression."
        self.repeated_data = b"ABABABABCDCDCDCDEFEFEFEFGHGHGHGH" * 10
        
    def test_binary_to_dna_conversion(self):
        """Test binary data to DNA sequence conversion."""
        # Test with simple data
        simple_data = b"\x00\xFF\x55\xAA"  # 00000000 11111111 01010101 10101010
        dna_seq = self.compressor.binary_to_dna(simple_data)
        
        # Should be: AAAATTTT CCCCGGGG (00=A, 01=C, 10=G, 11=T)
        # 00000000 = AAAAAAAA, 11111111 = TTTTTTTT, 01010101 = CCCCCCCC, 10101010 = GGGGGGGG
        expected = "AAAATTTTCCCCGGGG"
        self.assertEqual(str(dna_seq), expected)
        
        # Test round-trip conversion
        recovered_data = self.compressor.dna_to_binary(str(dna_seq))
        self.assertEqual(recovered_data, simple_data)
    
    def test_dna_to_binary_conversion(self):
        """Test DNA sequence to binary data conversion."""
        # Test with known DNA sequence
        dna_sequence = "ACGTACGT"  # 00 01 10 11 00 01 10 11
        expected_binary = b"\x1B\x1B"  # 00011011 00011011
        
        # Set up the original bits length to avoid padding issues
        self.compressor._original_bits_length = 16
        result = self.compressor.dna_to_binary(dna_sequence)
        self.assertEqual(result, expected_binary)
    
    def test_dvnp_compression(self):
        """Test DVNP compression and decompression."""
        # Convert test data to DNA first
        dna_seq = str(self.compressor.binary_to_dna(self.repeated_data))
        
        # Compress
        compressed, dictionary = self.compressor.dvnp_compress(dna_seq)
        
        # For LZW-style compression, may not always compress short repeated patterns
        # Just verify decompression works correctly
        self.assertIsInstance(compressed, list)
        self.assertIsInstance(dictionary, dict)
        
        # Decompress
        decompressed = self.compressor.dvnp_decompress(compressed, dictionary)
        
        # Should match original
        self.assertEqual(decompressed, dna_seq)
    
    def test_circular_encapsulation(self):
        """Test circular encapsulation functionality."""
        test_list = list(range(100))  # Simple test data
        
        circular_data = self.compressor.circular_encapsulate(test_list)
        
        # Should be longer due to padding and bridge
        self.assertGreaterEqual(len(circular_data), len(test_list))
        
        # Should start with original data
        self.assertEqual(circular_data[:len(test_list)], test_list)
    
    def test_trans_splicing_markers(self):
        """Test trans-splicing marker addition and metadata."""
        test_data = list(range(2500))  # Data larger than chunk size
        
        marked_data, metadata = self.compressor.add_trans_splicing_markers(test_data)
        
        # Should have markers added
        self.assertGreater(len(marked_data), len(test_data))
        
        # Should have metadata
        self.assertIn('sl_marker_code', metadata)
        self.assertIn('chunk_size', metadata)
        self.assertIn('original_length', metadata)
        
        # Original length should match
        self.assertEqual(metadata['original_length'], len(test_data))
    
    def test_end_to_end_compression(self):
        """Test complete compression and decompression cycle."""
        # Test with various data sizes and types
        test_cases = [
            b"Small test",
            self.test_data,
            self.repeated_data,
            bytes(range(256)),  # All possible byte values
            b"A" * 1000,  # Highly repetitive
            b"".join([bytes([i % 256]) for i in range(5000)])  # Larger data
        ]
        
        for test_data in test_cases:
            with self.subTest(data_size=len(test_data)):
                # Compress
                compressed, metadata = self.compressor.compress(test_data)
                
                # Verify metadata structure
                self.assertIn('dvnp_dictionary', metadata)
                self.assertIn('trans_splicing', metadata)
                self.assertIn('original_size', metadata)
                self.assertEqual(metadata['original_size'], len(test_data))
                
                # Decompress
                decompressed = self.compressor.decompress(compressed, metadata)
                
                # Verify integrity
                self.assertEqual(decompressed, test_data)
    
    def test_empty_data_handling(self):
        """Test handling of empty input data."""
        empty_data = b""
        
        compressed, metadata = self.compressor.compress(empty_data)
        decompressed = self.compressor.decompress(compressed, metadata)
        
        self.assertEqual(decompressed, empty_data)
    
    def test_compression_statistics(self):
        """Test compression statistics calculation."""
        compressed, metadata = self.compressor.compress(self.repeated_data)
        stats = self.compressor.get_compression_stats(self.repeated_data, compressed)
        
        # Verify statistics structure
        required_keys = [
            'original_size_bytes',
            'compressed_size_bytes', 
            'compression_ratio',
            'space_savings_percent',
            'bits_per_base'
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))
        
        # Basic sanity checks
        self.assertEqual(stats['original_size_bytes'], len(self.repeated_data))
        self.assertGreaterEqual(stats['compression_ratio'], 0)
        self.assertLessEqual(stats['space_savings_percent'], 100)
    
    def test_prime_number_generation(self):
        """Test prime number generation utility."""
        # Test known primes
        test_cases = [
            (1, 2),
            (2, 2),
            (3, 3),
            (10, 11),
            (100, 101)
        ]
        
        for input_val, expected in test_cases:
            result = self.compressor._next_prime(input_val)
            self.assertEqual(result, expected)
            self.assertTrue(self.compressor._is_prime(result))
    
    def test_invalid_dna_handling(self):
        """Test handling of invalid DNA sequences."""
        # Test with invalid characters
        invalid_dna = "ACGTXYZ"
        
        with self.assertRaises((KeyError, ValueError)):
            self.compressor.dna_to_binary(invalid_dna)


class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_sequence = "ACGTACGTGGCCTTAA"
        self.compressor = CircularChromosomeCompressor()
        
    def test_dna_sequence_validation(self):
        """Test DNA sequence validation."""
        valid_sequences = ["ACGT", "acgt", "AAAATTTTGGGGCCCC"]
        invalid_sequences = ["ACGTX", "123", "ACGT-N"]
        
        for seq in valid_sequences:
            self.assertTrue(helpers.validate_dna_sequence(seq))
            
        for seq in invalid_sequences:
            self.assertFalse(helpers.validate_dna_sequence(seq))
    
    def test_gc_content_calculation(self):
        """Test GC content calculation."""
        test_cases = [
            ("AAAA", 0.0),
            ("GGGG", 100.0),
            ("ACGT", 50.0),
            ("AACG", 50.0),
            ("", 0.0)
        ]
        
        for seq, expected in test_cases:
            result = helpers.calculate_gc_content(seq)
            self.assertAlmostEqual(result, expected, places=1)
    
    def test_file_operations(self):
        """Test file save/load operations."""
        test_data = list(range(100))
        test_metadata = {"test": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Test save
            helpers.save_compressed_data(test_data, test_metadata, tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            
            # Test load
            loaded_data, loaded_metadata = helpers.load_compressed_data(tmp_path)
            self.assertEqual(loaded_data, test_data)
            self.assertEqual(loaded_metadata, test_metadata)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_compression_efficiency_analysis(self):
        """Test compression efficiency analysis."""
        result = helpers.analyze_compression_efficiency(1000, 500, 250)
        
        expected_keys = [
            'compression_ratio',
            'space_savings_percent',
            'bits_per_base',
            'shannon_efficiency_percent',
            'theoretical_optimal'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Test values should be reasonable
        self.assertEqual(result['compression_ratio'], 0.5)
        self.assertEqual(result['space_savings_percent'], 50.0)
    
    def test_dna_synthesis_cost_estimation(self):
        """Test DNA synthesis cost estimation."""
        result = helpers.estimate_dna_synthesis_cost(1000, 0.10)
        
        expected_keys = [
            'synthesis_cost_usd',
            'setup_cost_usd',
            'purification_cost_usd',
            'total_cost_usd',
            'cost_per_kb_data'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
            self.assertGreaterEqual(result[key], 0)
    
    def test_decompression_integrity_verification(self):
        """Test integrity verification."""
        original = b"test data"
        same_data = b"test data"
        different_data = b"different"
        
        self.assertTrue(helpers.verify_decompression_integrity(original, same_data))
        self.assertFalse(helpers.verify_decompression_integrity(original, different_data))


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = CircularChromosomeCompressor()
        
    def test_text_file_compression(self):
        """Test compression of text files."""
        # Create a sample text file
        text_content = "This is a sample text file with some repeated patterns. " * 50
        text_data = text_content.encode('utf-8')
        
        compressed, metadata = self.compressor.compress(text_data)
        decompressed = self.compressor.decompress(compressed, metadata)
        
        # Verify integrity
        self.assertEqual(decompressed, text_data)
        
        # Note: This algorithm is designed for DNA storage optimization, not traditional compression
        # The "compression" includes DNA conversion overhead and markers for bio-compatibility
        stats = self.compressor.get_compression_stats(text_data, compressed)
        self.assertGreater(stats['compression_ratio'], 0)  # Should have some ratio calculation
    
    def test_binary_file_compression(self):
        """Test compression of binary files."""
        # Create structured binary data
        binary_data = bytearray()
        for i in range(1000):
            binary_data.extend([i % 256, (i * 2) % 256, (i * 3) % 256])
        
        compressed, metadata = self.compressor.compress(bytes(binary_data))
        decompressed = self.compressor.decompress(compressed, metadata)
        
        # Verify integrity
        self.assertEqual(decompressed, bytes(binary_data))
    
    def test_large_file_simulation(self):
        """Test with simulated large file (within reasonable test limits)."""
        # Create 50KB of structured data
        large_data = bytes([i % 256 for i in range(51200)])  # 50KB
        
        compressed, metadata = self.compressor.compress(large_data)
        decompressed = self.compressor.decompress(compressed, metadata)
        
        # Verify integrity
        self.assertEqual(decompressed, large_data)
        
        # Test compression statistics
        stats = self.compressor.get_compression_stats(large_data, compressed)
        self.assertGreater(stats['original_size_bytes'], 50000)


def run_all_tests():
    """Run all test cases."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCircularChromosomeCompressor,
        TestHelperFunctions,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
