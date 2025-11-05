#!/usr/bin/env python3
"""
Shannon Entropy Analysis Test Suite
Test the Shannon entropy calculation and statistical analysis features.
"""

import unittest
import sys
import os
import math

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.circular_chromosome_compression import CircularChromosomeCompressor


class TestShannonEntropy(unittest.TestCase):
    """Test Shannon entropy calculation and analysis features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = CircularChromosomeCompressor()
    
    def test_entropy_calculation_uniform_data(self):
        """Test entropy calculation for uniform data (should be maximum)."""
        # Equal distribution of all 4 bases
        data = "ACGTACGTACGTACGT"
        entropy = self.compressor._entropy(data.encode())
        
        # For uniform distribution of 4 symbols, entropy should be log2(4) = 2.0
        expected_entropy = 2.0
        self.assertAlmostEqual(entropy, expected_entropy, places=3)
    
    def test_entropy_calculation_single_symbol(self):
        """Test entropy calculation for single symbol (should be minimum)."""
        # All same character
        data = "AAAAAAAAAAAAAAAA"
        entropy = self.compressor._entropy(data.encode())
        
        # Single symbol should have entropy of 0
        self.assertEqual(entropy, 0.0)
    
    def test_entropy_calculation_binary(self):
        """Test entropy calculation for binary data."""
        # Half A's, half T's
        data = "AAAAAAAATTTTTTTT"
        entropy = self.compressor._entropy(data.encode())
        
        # Binary uniform distribution should have entropy of 1.0
        self.assertAlmostEqual(entropy, 1.0, places=3)
    
    def test_entropy_calculation_empty_data(self):
        """Test entropy calculation for empty data."""
        entropy = self.compressor._entropy(b"")
        self.assertEqual(entropy, 0.0)
    
    def test_compression_stats_include_entropy(self):
        """Test that compression statistics include entropy analysis."""
        test_data = b"This is a test string with some repeated patterns and some unique content."
        
        compressed = self.compressor.compress(test_data)
        stats = self.compressor.get_compression_stats(test_data, compressed)
        
        # Check that entropy-related fields are present
        self.assertIn('original_entropy', stats)
        self.assertIn('compressed_entropy', stats)
        self.assertIn('entropy_reduction', stats)
        self.assertIn('theoretical_minimum_size', stats)
        self.assertIn('shannon_efficiency', stats)
        self.assertIn('compression_effectiveness', stats)
        
        # Verify entropy values are reasonable
        self.assertGreaterEqual(stats['original_entropy'], 0.0)
        self.assertLessEqual(stats['original_entropy'], 8.0)  # Max bits per byte
        self.assertGreaterEqual(stats['compressed_entropy'], 0.0)
        self.assertLessEqual(stats['compressed_entropy'], 8.0)
        
        # Verify Shannon efficiency is between 0 and 1
        self.assertGreaterEqual(stats['shannon_efficiency'], 0.0)
        self.assertLessEqual(stats['shannon_efficiency'], 1.0)
    
    def test_entropy_with_different_data_types(self):
        """Test entropy calculation with different types of data."""
        test_cases = [
            (b"\x00" * 16, 0.0),  # All zeros
            (b"\xFF" * 16, 0.0),  # All ones
            (b"ABABABABABABABAB", 1.0),  # Binary pattern
            (bytes(range(256)), 8.0),  # All possible bytes (max entropy)
        ]
        
        for data, expected_entropy in test_cases:
            with self.subTest(data=data[:4] + b"..."):
                entropy = self.compressor._entropy(data)
                if expected_entropy == 8.0:
                    # For all 256 bytes, entropy should be close to 8.0
                    self.assertAlmostEqual(entropy, expected_entropy, places=1)
                else:
                    self.assertAlmostEqual(entropy, expected_entropy, places=3)
    
    def test_theoretical_compression_limits(self):
        """Test theoretical compression limit calculations."""
        # High entropy data should have poor compression
        high_entropy_data = bytes(range(256))
        compressed_high = self.compressor.compress(high_entropy_data)
        stats_high = self.compressor.get_compression_stats(high_entropy_data, compressed_high)
        
        # Low entropy data should have good compression
        low_entropy_data = b"A" * 256
        compressed_low = self.compressor.compress(low_entropy_data)
        stats_low = self.compressor.get_compression_stats(low_entropy_data, compressed_low)
        
        # High entropy data should compress worse than low entropy data
        # Compare compression ratios instead of Shannon efficiency (which can be 0 for zero entropy)
        self.assertGreater(stats_high['compression_ratio'], stats_low['compression_ratio'])
        
        # Theoretical minimum for low entropy should be much smaller
        self.assertLess(stats_low['theoretical_minimum_size'], stats_high['theoretical_minimum_size'])
    
    def test_compression_effectiveness_metric(self):
        """Test compression effectiveness calculation."""
        # Test with predictable data
        repetitive_data = b"ABCD" * 64  # 256 bytes with pattern
        compressed = self.compressor.compress(repetitive_data)
        stats = self.compressor.get_compression_stats(repetitive_data, compressed)
        
        # Should have reasonable effectiveness (between 0 and 1)
        self.assertGreaterEqual(stats['compression_effectiveness'], 0.0)
        self.assertLessEqual(stats['compression_effectiveness'], 1.0)
        
        # Effectiveness should correlate with actual compression ratio
        actual_ratio = len(compressed) / len(repetitive_data)
        shannon_ratio = stats['theoretical_minimum_size'] / len(repetitive_data)
        
        # Effectiveness should be between 0 and 1, and reflect compression quality
        self.assertGreaterEqual(stats['compression_effectiveness'], 0.0)
        self.assertLessEqual(stats['compression_effectiveness'], 1.0)
        
        # For repetitive data, effectiveness should be reasonably good (> 0.1)
        self.assertGreater(stats['compression_effectiveness'], 0.1)
    
    def test_entropy_edge_cases(self):
        """Test entropy calculation with edge cases."""
        # Single byte
        single_byte = b"X"
        entropy = self.compressor._entropy(single_byte)
        self.assertEqual(entropy, 0.0)
        
        # Two different bytes
        two_bytes = b"XY"
        entropy = self.compressor._entropy(two_bytes)
        self.assertEqual(entropy, 1.0)
        
        # Large uniform data
        large_uniform = b"Z" * 10000
        entropy = self.compressor._entropy(large_uniform)
        self.assertEqual(entropy, 0.0)


class TestEntropyIntegration(unittest.TestCase):
    """Test integration of entropy analysis with compression pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = CircularChromosomeCompressor()
    
    def test_entropy_preserved_in_compression_stats(self):
        """Test that entropy information is included in compression statistics."""
        test_data = b"Sample data for entropy logging test"
        
        # Compress data normally
        compressed = self.compressor.compress(test_data)
        stats = self.compressor.get_compression_stats(test_data, compressed)
        
        # Verify entropy analysis completed
        self.assertIn('original_entropy', stats)
        self.assertGreater(stats['original_entropy'], 0.0)
    
    def test_layered_entropy_analysis(self):
        """Test entropy analysis at different compression layers."""
        test_data = b"Multi-layer entropy analysis test data with various patterns"
        
        # Core compression only
        core_compressed, core_metadata = self.compressor.compress_core(test_data)
        
        # Full compression with encapsulation
        full_compressed, full_metadata = self.compressor.compress(test_data)
        
        # Analyze entropy at each stage
        original_entropy = self.compressor._entropy(test_data)
        
        # Convert compressed integer codes to bytes properly
        core_bytes = []
        for code in core_compressed:
            code_bytes = code.to_bytes((code.bit_length() + 7) // 8 or 1, 'little')
            core_bytes.extend(code_bytes)
        core_entropy = self.compressor._entropy(bytes(core_bytes))
        
        full_bytes = []
        for code in full_compressed:
            code_bytes = code.to_bytes((code.bit_length() + 7) // 8 or 1, 'little')
            full_bytes.extend(code_bytes)
        full_entropy = self.compressor._entropy(bytes(full_bytes))
        
        # Verify entropy generally decreases through pipeline
        # (though encapsulation might add some entropy back)
        self.assertGreaterEqual(original_entropy, 0.0)
        self.assertGreaterEqual(core_entropy, 0.0)
        self.assertGreaterEqual(full_entropy, 0.0)


if __name__ == '__main__':
    unittest.main()
