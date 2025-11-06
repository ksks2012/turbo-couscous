/**
 * Test program for Circular Chromosome Compression (CCC) C++ implementation
 */

#include "circular_chromosome_compression.h"
#include <iostream>
#include <vector>
#include <string>
#include <cassert>
#include <chrono>

using namespace ccc;

void test_basic_compression() {
    std::cout << "\n=== Basic Compression Test ===" << std::endl;
    
    CircularChromosomeCompressor compressor(1000, 4, true, true);
    
    // Test data
    std::string test_string = "Hello, World! This is a test of the CCC algorithm.";
    std::vector<uint8_t> test_data(test_string.begin(), test_string.end());
    
    std::cout << "Original data size: " << test_data.size() << " bytes" << std::endl;
    std::cout << "Original data: " << test_string << std::endl;
    
    // Compress
    auto start = std::chrono::high_resolution_clock::now();
    auto [compressed_data, metadata] = compressor.compress(test_data);
    auto compress_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Compressed to " << compressed_data.size() << " codes" << std::endl;
    std::cout << "Compression time: " << 
                 std::chrono::duration_cast<std::chrono::microseconds>(compress_time).count() 
              << " microseconds" << std::endl;
    
    // Decompress
    start = std::chrono::high_resolution_clock::now();
    std::vector<uint8_t> decompressed_data = compressor.decompress(compressed_data, metadata);
    auto decompress_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Decompressed to " << decompressed_data.size() << " bytes" << std::endl;
    std::cout << "Decompression time: " << 
                 std::chrono::duration_cast<std::chrono::microseconds>(decompress_time).count() 
              << " microseconds" << std::endl;
    
    // Verify
    std::string decompressed_string(decompressed_data.begin(), decompressed_data.end());
    std::cout << "Decompressed data: " << decompressed_string << std::endl;
    
    if (test_data == decompressed_data) {
        std::cout << "✓ Compression/decompression successful!" << std::endl;
    } else {
        std::cout << "✗ Compression/decompression failed!" << std::endl;
        exit(1);
    }
    
    // Statistics
    CompressionStats stats = compressor.get_compression_stats(test_data, compressed_data, metadata);
    std::cout << "\nCompression Statistics:" << std::endl;
    std::cout << "  Compression ratio: " << stats.compression_ratio << std::endl;
    std::cout << "  Space savings: " << stats.space_savings_percent << "%" << std::endl;
    std::cout << "  Original entropy: " << stats.original_entropy << " bits/byte" << std::endl;
    std::cout << "  Compressed entropy: " << stats.compressed_entropy << " bits/byte" << std::endl;
    std::cout << "  Shannon efficiency: " << stats.shannon_efficiency << std::endl;
}

void test_dna_conversion() {
    std::cout << "\n=== DNA Conversion Test ===" << std::endl;
    
    CircularChromosomeCompressor compressor(1000, 4, true, true);
    
    // Test binary to DNA and back
    std::vector<uint8_t> test_binary = {0x41, 0x42, 0x43, 0x44}; // "ABCD"
    
    std::cout << "Original binary: ";
    for (uint8_t byte : test_binary) {
        std::cout << std::hex << static_cast<int>(byte) << " ";
    }
    std::cout << std::endl;
    
    std::string dna_seq = compressor.binary_to_dna(test_binary);
    std::cout << "DNA sequence: " << dna_seq << std::endl;
    
    std::vector<uint8_t> recovered_binary = compressor.dna_to_binary(dna_seq);
    
    std::cout << "Recovered binary: ";
    for (uint8_t byte : recovered_binary) {
        std::cout << std::hex << static_cast<int>(byte) << " ";
    }
    std::cout << std::endl;
    
    if (test_binary == recovered_binary) {
        std::cout << "✓ DNA conversion successful!" << std::endl;
    } else {
        std::cout << "✗ DNA conversion failed!" << std::endl;
        exit(1);
    }
}

void test_dvnp_compression() {
    std::cout << "\n=== DVNP Compression Test ===" << std::endl;
    
    CircularChromosomeCompressor compressor(1000, 4, true, true);
    
    // Test DVNP compression with repetitive DNA sequence
    std::string test_dna = "ATCGATCGATCGATCGAAAAAATCGATCGATCG";
    
    std::cout << "Original DNA: " << test_dna << std::endl;
    std::cout << "Length: " << test_dna.length() << std::endl;
    
    std::vector<int> compressed = compressor.dvnp_compress(test_dna);
    
    std::cout << "Compressed codes: ";
    for (size_t i = 0; i < std::min(compressed.size(), size_t(20)); ++i) {
        std::cout << compressed[i] << " ";
    }
    if (compressed.size() > 20) {
        std::cout << "... (" << compressed.size() << " total)";
    }
    std::cout << std::endl;
    
    std::string decompressed = compressor.dvnp_decompress(compressed);
    std::cout << "Decompressed: " << decompressed << std::endl;
    
    if (test_dna == decompressed) {
        std::cout << "✓ DVNP compression successful!" << std::endl;
    } else {
        std::cout << "✗ DVNP compression failed!" << std::endl;
        std::cout << "Expected: " << test_dna << std::endl;
        std::cout << "Got:      " << decompressed << std::endl;
        exit(1);
    }
}

void test_large_data() {
    std::cout << "\n=== Large Data Test ===" << std::endl;
    
    CircularChromosomeCompressor compressor(1000, 4, true, false); // Less verbose for large test
    
    // Generate large test data (10KB of repetitive pattern)
    std::string pattern = "The quick brown fox jumps over the lazy dog. ";
    std::string large_string;
    while (large_string.length() < 10240) {
        large_string += pattern;
    }
    
    std::vector<uint8_t> large_data(large_string.begin(), large_string.end());
    
    std::cout << "Large data size: " << large_data.size() << " bytes" << std::endl;
    
    // Compress
    auto start = std::chrono::high_resolution_clock::now();
    auto [compressed_data, metadata] = compressor.compress(large_data);
    auto compress_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Compressed to " << compressed_data.size() << " codes" << std::endl;
    std::cout << "Compression time: " << 
                 std::chrono::duration_cast<std::chrono::milliseconds>(compress_time).count() 
              << " ms" << std::endl;
    
    // Decompress
    start = std::chrono::high_resolution_clock::now();
    std::vector<uint8_t> decompressed_data = compressor.decompress(compressed_data, metadata);
    auto decompress_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Decompressed to " << decompressed_data.size() << " bytes" << std::endl;
    std::cout << "Decompression time: " << 
                 std::chrono::duration_cast<std::chrono::milliseconds>(decompress_time).count() 
              << " ms" << std::endl;
    
    if (large_data == decompressed_data) {
        std::cout << "✓ Large data compression successful!" << std::endl;
    } else {
        std::cout << "✗ Large data compression failed!" << std::endl;
        exit(1);
    }
    
    // Statistics
    CompressionStats stats = compressor.get_compression_stats(large_data, compressed_data, metadata);
    std::cout << "\nLarge Data Compression Statistics:" << std::endl;
    std::cout << "  Compression ratio: " << stats.compression_ratio << std::endl;
    std::cout << "  Space savings: " << stats.space_savings_percent << "%" << std::endl;
    std::cout << "  Bits per base: " << stats.bits_per_base << std::endl;
}

int main() {
    std::cout << "Circular Chromosome Compression (CCC) C++ Test Suite" << std::endl;
    std::cout << "===================================================" << std::endl;
    
    try {
        test_dna_conversion();
        test_dvnp_compression();
        test_basic_compression();
        test_large_data();
        
        std::cout << "\n🎉 All tests passed successfully!" << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "\n❌ Test failed with exception: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
