/**
 * Example usage of Circular Chromosome Compression (CCC) C++ library
 */

#include "circular_chromosome_compression.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <iomanip>
#include <chrono>

using namespace ccc;

void compress_text_example() {
    std::cout << "\n=== Text Compression Example ===" << std::endl;
    
    // Create compressor instance
    CircularChromosomeCompressor compressor(1000, 4, true, true);
    
    // Sample text to compress
    std::string text = "Circular Chromosome Compression (CCC) is a bio-inspired algorithm "
                      "that mimics the compression mechanisms found in dinoflagellate organisms. "
                      "This algorithm converts binary data to DNA sequences and uses advanced "
                      "compression techniques including DVNP-like compression and trans-splicing.";
    
    // Convert string to byte vector
    std::vector<uint8_t> data(text.begin(), text.end());
    
    std::cout << "Original text (" << data.size() << " bytes):" << std::endl;
    std::cout << text << std::endl;
    
    // Compress the data
    auto [compressed_data, metadata] = compressor.compress(data);
    
    std::cout << "\nCompressed to " << compressed_data.size() << " codes" << std::endl;
    
    // Get compression statistics
    CompressionStats stats = compressor.get_compression_stats(data, compressed_data, metadata);
    
    std::cout << "\nCompression Statistics:" << std::endl;
    std::cout << "  Original size: " << stats.original_size_bytes << " bytes" << std::endl;
    std::cout << "  Compressed size: " << stats.compressed_size_bytes << " bytes" << std::endl;
    std::cout << "  Compression ratio: " << std::fixed << std::setprecision(3) 
              << stats.compression_ratio << std::endl;
    std::cout << "  Space savings: " << std::fixed << std::setprecision(1) 
              << stats.space_savings_percent << "%" << std::endl;
    std::cout << "  Original entropy: " << std::fixed << std::setprecision(3) 
              << stats.original_entropy << " bits/byte" << std::endl;
    std::cout << "  Shannon efficiency: " << std::fixed << std::setprecision(3) 
              << stats.shannon_efficiency << std::endl;
    
    // Decompress the data
    std::vector<uint8_t> decompressed_data = compressor.decompress(compressed_data, metadata);
    
    // Verify the result
    std::string decompressed_text(decompressed_data.begin(), decompressed_data.end());
    
    if (text == decompressed_text) {
        std::cout << "\n✓ Compression and decompression successful!" << std::endl;
    } else {
        std::cout << "\n✗ Compression/decompression failed!" << std::endl;
    }
}

void compress_file_example(const std::string& filename) {
    std::cout << "\n=== File Compression Example ===" << std::endl;
    
    // Read file
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cout << "Cannot open file: " << filename << std::endl;
        return;
    }
    
    std::vector<uint8_t> file_data((std::istreambuf_iterator<char>(file)),
                                   std::istreambuf_iterator<char>());
    file.close();
    
    if (file_data.empty()) {
        std::cout << "File is empty or could not be read: " << filename << std::endl;
        return;
    }
    
    std::cout << "File: " << filename << std::endl;
    std::cout << "Original size: " << file_data.size() << " bytes" << std::endl;
    
    // Create compressor (disable verbose for file compression)
    CircularChromosomeCompressor compressor(1000, 4, true, false);
    
    // Compress
    auto start = std::chrono::high_resolution_clock::now();
    auto [compressed_data, metadata] = compressor.compress(file_data);
    auto compress_time = std::chrono::high_resolution_clock::now() - start;
    
    // Calculate compression statistics
    CompressionStats stats = compressor.get_compression_stats(file_data, compressed_data, metadata);
    
    std::cout << "Compressed size: " << stats.compressed_size_bytes << " bytes" << std::endl;
    std::cout << "Compression ratio: " << std::fixed << std::setprecision(3) 
              << stats.compression_ratio << std::endl;
    std::cout << "Space savings: " << std::fixed << std::setprecision(1) 
              << stats.space_savings_percent << "%" << std::endl;
    std::cout << "Compression time: " << 
                 std::chrono::duration_cast<std::chrono::milliseconds>(compress_time).count() 
              << " ms" << std::endl;
    
    // Decompress to verify
    start = std::chrono::high_resolution_clock::now();
    std::vector<uint8_t> decompressed_data = compressor.decompress(compressed_data, metadata);
    auto decompress_time = std::chrono::high_resolution_clock::now() - start;
    
    std::cout << "Decompression time: " << 
                 std::chrono::duration_cast<std::chrono::milliseconds>(decompress_time).count() 
              << " ms" << std::endl;
    
    // Verify integrity
    if (file_data == decompressed_data) {
        std::cout << "✓ File compression/decompression successful!" << std::endl;
        
        // Optional: Save compressed data to file
        std::string compressed_filename = filename + ".ccc";
        std::ofstream outfile(compressed_filename, std::ios::binary);
        if (outfile.is_open()) {
            // Simple format: save metadata size, metadata, data size, data
            // This is just for demonstration - real implementation would use proper serialization
            size_t metadata_size = sizeof(metadata);
            outfile.write(reinterpret_cast<const char*>(&metadata_size), sizeof(metadata_size));
            outfile.write(reinterpret_cast<const char*>(&metadata), sizeof(metadata));
            
            size_t data_size = compressed_data.size();
            outfile.write(reinterpret_cast<const char*>(&data_size), sizeof(data_size));
            outfile.write(reinterpret_cast<const char*>(compressed_data.data()), 
                         data_size * sizeof(int));
            outfile.close();
            
            std::cout << "Compressed data saved to: " << compressed_filename << std::endl;
        }
    } else {
        std::cout << "✗ File compression/decompression failed!" << std::endl;
    }
}

void show_algorithm_info() {
    std::cout << "Circular Chromosome Compression (CCC) Algorithm" << std::endl;
    std::cout << "==============================================" << std::endl;
    std::cout << "\nBio-inspired by dinoflagellate circular chromosomes and histone-free condensation." << std::endl;
    std::cout << "\nKey Features:" << std::endl;
    std::cout << "• Binary-to-DNA conversion using 2-bit nucleotide encoding" << std::endl;
    std::cout << "• DVNP-like compression with dynamic dictionary reset" << std::endl;
    std::cout << "• Circular encapsulation to eliminate boundary waste" << std::endl;
    std::cout << "• Trans-splicing markers for error correction" << std::endl;
    std::cout << "• Layered architecture for modularity" << std::endl;
    std::cout << "• Shannon entropy analysis for compression efficiency" << std::endl;
    
    std::cout << "\nAlgorithm Pipeline:" << std::endl;
    std::cout << "1. Binary Data → DNA Sequence (2-bit encoding)" << std::endl;
    std::cout << "2. DNA Sequence → DVNP Compression (LZW-based)" << std::endl;
    std::cout << "3. Compressed Data → Circular Encapsulation" << std::endl;
    std::cout << "4. Circular Data → Trans-splicing Markers" << std::endl;
    std::cout << "5. Hash-based integrity verification" << std::endl;
}

int main(int argc, char* argv[]) {
    show_algorithm_info();
    
    try {
        // Example 1: Text compression
        compress_text_example();
        
        // Example 2: File compression (if file provided)
        if (argc > 1) {
            compress_file_example(argv[1]);
        } else {
            std::cout << "\n=== Usage ===" << std::endl;
            std::cout << "To compress a file, run: " << argv[0] << " <filename>" << std::endl;
            
            // Try to compress this source file as an example
            compress_file_example("example_usage.cpp");
        }
        
    } catch (const std::exception& e) {
        std::cout << "\nError: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
