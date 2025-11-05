#!/usr/bin/env python3
"""
Test hash verification and data integrity checking functionality.
"""

import unittest
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.circular_chromosome_compression import CircularChromosomeCompressor


class TestHashVerification(unittest.TestCase):
    """Test hash verification and data integrity checking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor_strict = CircularChromosomeCompressor(strict_mode=True, verbose=True)
        self.compressor_lenient = CircularChromosomeCompressor(strict_mode=False, verbose=True)
    
    def test_hash_computation(self):
        """Test basic hash computation functionality."""
        test_data = [1, 2, 3, 4, 5]
        hash_value = self.compressor_strict._compute_data_hash(test_data)
        
        # Hash should be 8 characters
        self.assertEqual(len(hash_value), 8)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_value))
        
        # Same data should produce same hash
        hash_value2 = self.compressor_strict._compute_data_hash(test_data)
        self.assertEqual(hash_value, hash_value2)
        
        # Different data should produce different hash
        different_data = [1, 2, 3, 4, 6]
        different_hash = self.compressor_strict._compute_data_hash(different_data)
        self.assertNotEqual(hash_value, different_hash)
    
    def test_hash_computation_empty_data(self):
        """Test hash computation with empty data."""
        empty_hash = self.compressor_strict._compute_data_hash([])
        self.assertEqual(empty_hash, "")
    
    def test_data_integrity_verification_success(self):
        """Test successful data integrity verification."""
        test_data = [10, 20, 30, 40]
        expected_hash = self.compressor_strict._compute_data_hash(test_data)
        
        # Should return True for correct hash
        result = self.compressor_strict._verify_data_integrity(test_data, expected_hash, "test")
        self.assertTrue(result)
    
    def test_data_integrity_verification_failure_strict_mode(self):
        """Test data integrity verification failure in strict mode."""
        test_data = [10, 20, 30, 40]
        wrong_hash = "12345678"
        
        # Should raise exception in strict mode
        with self.assertRaises(ValueError) as context:
            self.compressor_strict._verify_data_integrity(test_data, wrong_hash, "test")
        
        self.assertIn("Data integrity check failed", str(context.exception))
        self.assertIn("hash mismatch", str(context.exception))
    
    def test_data_integrity_verification_failure_lenient_mode(self):
        """Test data integrity verification failure in lenient mode."""
        test_data = [10, 20, 30, 40]
        wrong_hash = "12345678"
        
        # Should return False in lenient mode (no exception)
        result = self.compressor_lenient._verify_data_integrity(test_data, wrong_hash, "test")
        self.assertFalse(result)
    
    def test_data_integrity_no_hash(self):
        """Test data integrity verification when no hash is provided."""
        test_data = [10, 20, 30, 40]
        
        # Should return False when no hash provided
        result = self.compressor_strict._verify_data_integrity(test_data, "", "test")
        self.assertFalse(result)
    
    def test_end_to_end_integrity_check_success(self):
        """Test end-to-end compression/decompression with integrity check."""
        test_data = b"This is test data for integrity verification."
        
        # Compress data
        compressed, metadata = self.compressor_strict.compress(test_data)
        
        # Verify hash is stored in metadata
        self.assertIn('trans_splicing', metadata['encapsulation'])
        self.assertIn('data_hash', metadata['encapsulation']['trans_splicing'])
        self.assertTrue(len(metadata['encapsulation']['trans_splicing']['data_hash']) == 8)
        
        # Decompress should succeed with correct metadata
        decompressed = self.compressor_strict.decompress(compressed, metadata)
        self.assertEqual(test_data, decompressed)
    
    def test_end_to_end_integrity_check_failure(self):
        """Test end-to-end decompression with corrupted hash."""
        test_data = b"This is test data for integrity verification."
        
        # Compress data
        compressed, metadata = self.compressor_strict.compress(test_data)
        
        # Corrupt the hash in metadata
        metadata['encapsulation']['trans_splicing']['data_hash'] = "corrupted"
        
        # Decompression should fail in strict mode
        with self.assertRaises(ValueError) as context:
            self.compressor_strict.decompress(compressed, metadata)
        
        self.assertIn("Data integrity check failed", str(context.exception))
    
    def test_end_to_end_integrity_check_lenient_mode(self):
        """Test end-to-end decompression with corrupted hash in lenient mode."""
        test_data = b"This is test data for integrity verification."
        
        # Compress data
        compressed, metadata = self.compressor_lenient.compress(test_data)
        
        # Corrupt the hash in metadata
        original_hash = metadata['encapsulation']['trans_splicing']['data_hash']
        metadata['encapsulation']['trans_splicing']['data_hash'] = "corrupted"
        
        # Decompression should succeed in lenient mode despite hash mismatch
        decompressed = self.compressor_lenient.decompress(compressed, metadata)
        self.assertEqual(test_data, decompressed)
    
    def test_integrity_check_with_different_data_sizes(self):
        """Test integrity checking with different data sizes."""
        test_cases = [
            b"A",  # Single byte
            b"AB" * 50,  # 100 bytes
            b"ABC" * 333,  # ~1000 bytes
            b"Test data with special chars: !@#$%^&*()",
            bytes(range(256)),  # All byte values
        ]
        
        for test_data in test_cases:
            with self.subTest(data_size=len(test_data)):
                # Compress and decompress
                compressed, metadata = self.compressor_strict.compress(test_data)
                decompressed = self.compressor_strict.decompress(compressed, metadata)
                
                # Verify integrity maintained
                self.assertEqual(test_data, decompressed)
                
                # Verify hash is present
                hash_value = metadata['encapsulation']['trans_splicing']['data_hash']
                self.assertEqual(len(hash_value), 8)
    
    def test_hash_verification_during_decapsulation(self):
        """Test hash verification specifically during decapsulation step."""
        test_data = b"Test decapsulation hash verification"
        
        # Get intermediate compression stages
        core_compressed, core_metadata = self.compressor_strict.compress_core(test_data)
        encapsulated, encap_metadata = self.compressor_strict.encapsulate(core_compressed)
        
        # Verify hash exists in encapsulation metadata
        self.assertIn('data_hash', encap_metadata['trans_splicing'])
        
        # Decapsulation should verify hash successfully
        decapsulated = self.compressor_strict.decapsulate(encapsulated, encap_metadata)
        self.assertEqual(core_compressed, decapsulated)
        
        # Test with corrupted hash
        corrupted_metadata = encap_metadata.copy()
        corrupted_metadata['trans_splicing'] = corrupted_metadata['trans_splicing'].copy()
        corrupted_metadata['trans_splicing']['data_hash'] = "badHash1"
        
        # Should fail in strict mode
        with self.assertRaises(ValueError):
            self.compressor_strict.decapsulate(encapsulated, corrupted_metadata)


if __name__ == '__main__':
    unittest.main()
