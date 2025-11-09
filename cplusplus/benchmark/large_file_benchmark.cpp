/**
 * Large file performance test for CCC C++ implementation
 * Tests files up to 100MB to evaluate scalability and performance
 */

#include "circular_chromosome_compression.h"
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <algorithm>
#include <random>
#include <cstdint>
#include <memory>

using namespace ccc;
using namespace std::chrono;

struct TestResult {
    size_t size_mb = 0;
    std::string pattern;
    double compression_time_sec = 0.0;
    double decompression_time_sec = 0.0;
    double compression_throughput_mb_s = 0.0;
    double decompression_throughput_mb_s = 0.0;
    double compression_ratio = 0.0;
    double compressed_size_mb = 0.0;
    double bits_per_base = 0.0;
    bool integrity_verified = false;
    std::string error_message;
};

class LargeFileTestDataGenerator {
public:
    static std::vector<uint8_t> create_test_data(size_t size, const std::string& pattern) {
        std::cout << "  Generating " << (size / 1048576) << "MB test data (" << pattern << ")..." << std::flush;
        
        std::vector<uint8_t> data;
        data.reserve(size);
        
        if (pattern == "mixed") {
            data = create_mixed_pattern_data(size);
        } else if (pattern == "repetitive") {
            data = create_repetitive_data(size);
        } else if (pattern == "random") {
            data = create_random_data(size);
        } else if (pattern == "text") {
            data = create_text_data(size);
        } else { // sequential
            data = create_sequential_data(size);
        }
        
        std::cout << " Done." << std::endl;
        return data;
    }

private:
    static std::vector<uint8_t> create_mixed_pattern_data(size_t size) {
        std::vector<uint8_t> data;
        data.reserve(size);
        
        // Create different chunk patterns
        std::vector<std::vector<uint8_t>> chunk_patterns;
        
        // Text-like data chunk
        std::string text_chunk;
        for (int i = 0; i < 100; ++i) {
            text_chunk += "TEXT_DATA_CHUNK";
        }
        std::vector<uint8_t> text_pattern(text_chunk.begin(), text_chunk.end());
        chunk_patterns.push_back(text_pattern);
        
        // Binary sequence chunk
        std::vector<uint8_t> binary_pattern;
        for (int i = 0; i < 4; ++i) {
            for (int j = 0; j < 256; ++j) {
                binary_pattern.push_back(static_cast<uint8_t>(j));
            }
        }
        chunk_patterns.push_back(binary_pattern);
        
        // Zero blocks
        std::vector<uint8_t> zero_pattern(1000, 0);
        chunk_patterns.push_back(zero_pattern);
        
        // Repetitive patterns
        std::string repeat_str;
        for (int i = 0; i < 200; ++i) {
            repeat_str += "REPEAT";
        }
        std::vector<uint8_t> repeat_pattern(repeat_str.begin(), repeat_str.end());
        chunk_patterns.push_back(repeat_pattern);
        
        const size_t chunk_size = 4096; // 4KB chunks
        for (size_t i = 0; i < size; i += chunk_size) {
            size_t pattern_idx = (i / chunk_size) % chunk_patterns.size();
            const auto& chunk = chunk_patterns[pattern_idx];
            size_t remaining = std::min(chunk_size, size - i);
            
            // Repeat pattern to fill chunk
            for (size_t j = 0; j < remaining; ++j) {
                data.push_back(chunk[j % chunk.size()]);
            }
        }
        
        return data;
    }
    
    static std::vector<uint8_t> create_repetitive_data(size_t size) {
        std::string base_pattern;
        for (int i = 0; i < 64; ++i) {
            base_pattern += "ABCDEFGHIJKLMNOP";
        }
        std::vector<uint8_t> data;
        data.reserve(size);
        
        for (size_t i = 0; i < size; ++i) {
            data.push_back(static_cast<uint8_t>(base_pattern[i % base_pattern.length()]));
        }
        
        return data;
    }
    
    static std::vector<uint8_t> create_random_data(size_t size) {
        std::vector<uint8_t> data;
        data.reserve(size);
        
        // Use deterministic "random" data for consistent testing
        for (size_t i = 0; i < size; ++i) {
            data.push_back(static_cast<uint8_t>((i * 17 + 23) % 256));
        }
        
        return data;
    }
    
    static std::vector<uint8_t> create_text_data(size_t size) {
        std::string text_block;
        for (int i = 0; i < 100; ++i) {
            text_block += "Lorem ipsum dolor sit amet, consectetur adipiscing elit. ";
        }
        std::vector<uint8_t> data;
        data.reserve(size);
        
        for (size_t i = 0; i < size; ++i) {
            data.push_back(static_cast<uint8_t>(text_block[i % text_block.length()]));
        }
        
        return data;
    }
    
    static std::vector<uint8_t> create_sequential_data(size_t size) {
        std::vector<uint8_t> data;
        data.reserve(size);
        
        for (size_t i = 0; i < size; ++i) {
            data.push_back(static_cast<uint8_t>(i % 256));
        }
        
        return data;
    }
};

class LargeFileBenchmark {
private:
    CircularChromosomeCompressor compressor_;
    
public:
    LargeFileBenchmark() : compressor_(10000, 4, true, false) { // Larger chunks for big files
    }
    
    TestResult run_single_test(size_t size, const std::string& pattern) {
        TestResult result;
        result.size_mb = size / 1048576;
        result.pattern = pattern;
        
        try {
            // Generate test data
            auto test_data = LargeFileTestDataGenerator::create_test_data(size, pattern);
            
            // Compression test
            std::cout << "  Compressing..." << std::flush;
            auto start_time = high_resolution_clock::now();
            
            auto [compressed_data, metadata] = compressor_.compress(test_data);
            
            auto end_time = high_resolution_clock::now();
            result.compression_time_sec = duration_cast<microseconds>(end_time - start_time).count() / 1000000.0;
            std::cout << " Done." << std::endl;
            
            // Calculate compression stats
            auto stats = compressor_.get_compression_stats(test_data, compressed_data, metadata);
            result.compression_ratio = stats.compression_ratio;
            result.compressed_size_mb = stats.compressed_size_bytes / 1048576.0;
            result.bits_per_base = stats.bits_per_base;
            
            // Decompression test
            std::cout << "  Decompressing..." << std::flush;
            start_time = high_resolution_clock::now();
            
            auto decompressed_data = compressor_.decompress(compressed_data, metadata);
            
            end_time = high_resolution_clock::now();
            result.decompression_time_sec = duration_cast<microseconds>(end_time - start_time).count() / 1000000.0;
            std::cout << " Done." << std::endl;
            
            // Verify integrity
            result.integrity_verified = (test_data == decompressed_data);
            
            // Calculate throughput
            result.compression_throughput_mb_s = result.size_mb / result.compression_time_sec;
            result.decompression_throughput_mb_s = result.size_mb / result.decompression_time_sec;
            
            std::cout << "  ✓ Compression: " << std::fixed << std::setprecision(2) 
                      << result.compression_throughput_mb_s << " MB/s" << std::endl;
            std::cout << "  ✓ Decompression: " << std::fixed << std::setprecision(2) 
                      << result.decompression_throughput_mb_s << " MB/s" << std::endl;
            std::cout << "  ✓ Ratio: " << std::fixed << std::setprecision(3) 
                      << result.compression_ratio << std::endl;
            std::cout << "  ✓ Integrity: " << (result.integrity_verified ? "PASS" : "FAIL") << std::endl;
            
        } catch (const std::exception& e) {
            result.error_message = e.what();
            std::cout << "  ✗ Error: " << e.what() << std::endl;
        }
        
        return result;
    }
    
    void run_all_tests() {
        std::cout << "=== CCC C++ Large File Performance Test ===" << std::endl;
        
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::cout << "Timestamp: " << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << std::endl;
        std::cout << std::endl;
        
        // Test sizes from 1MB to 100MB
        std::vector<size_t> test_sizes = {
            1048576,    // 1MB
            5242880,    // 5MB
            10485760,   // 10MB
            20971520,   // 20MB
            52428800,   // 50MB
            104857600,  // 100MB
        };
        
        std::vector<std::string> test_patterns = {"mixed", "repetitive", "text"};
        
        std::vector<TestResult> results;
        
        for (size_t size : test_sizes) {
            size_t size_mb = size / 1048576;
            std::cout << "\n=== Testing " << size_mb << "MB files ===" << std::endl;
            
            for (const auto& pattern : test_patterns) {
                std::cout << "Pattern: " << pattern << std::endl;
                
                TestResult result = run_single_test(size, pattern);
                results.push_back(result);
            }
        }
        
        // Generate summary report
        print_summary(results);
        save_results(results);
    }
    
private:
    void print_summary(const std::vector<TestResult>& results) {
        std::cout << "\n=== Performance Summary ===" << std::endl;
        std::cout << std::left << std::setw(8) << "Size" 
                  << std::setw(12) << "Pattern" 
                  << std::setw(12) << "Comp MB/s" 
                  << std::setw(14) << "Decomp MB/s" 
                  << std::setw(8) << "Ratio" 
                  << "Status" << std::endl;
        std::cout << std::string(80, '-') << std::endl;
        
        std::vector<TestResult> successful_tests;
        for (const auto& result : results) {
            if (result.error_message.empty() && result.integrity_verified) {
                successful_tests.push_back(result);
                
                std::cout << std::right << std::setw(4) << result.size_mb << "MB   "
                          << std::left << std::setw(12) << result.pattern
                          << std::right << std::setw(8) << std::fixed << std::setprecision(2) 
                          << result.compression_throughput_mb_s << "     "
                          << std::setw(10) << std::fixed << std::setprecision(2) 
                          << result.decompression_throughput_mb_s << "      "
                          << std::setw(5) << std::fixed << std::setprecision(3) 
                          << result.compression_ratio << "   ✓" << std::endl;
            }
        }
        
        if (!successful_tests.empty()) {
            // Calculate averages
            double avg_comp_speed = 0.0, avg_decomp_speed = 0.0, avg_ratio = 0.0;
            
            for (const auto& result : successful_tests) {
                avg_comp_speed += result.compression_throughput_mb_s;
                avg_decomp_speed += result.decompression_throughput_mb_s;
                avg_ratio += result.compression_ratio;
            }
            
            avg_comp_speed /= successful_tests.size();
            avg_decomp_speed /= successful_tests.size();
            avg_ratio /= successful_tests.size();
            
            std::cout << "\nAverage Performance:" << std::endl;
            std::cout << "  Compression speed: " << std::fixed << std::setprecision(2) 
                      << avg_comp_speed << " MB/s" << std::endl;
            std::cout << "  Decompression speed: " << std::fixed << std::setprecision(2) 
                      << avg_decomp_speed << " MB/s" << std::endl;
            std::cout << "  Compression ratio: " << std::fixed << std::setprecision(3) 
                      << avg_ratio << std::endl;
        }
        
        double success_rate = results.empty() ? 0.0 : 
                             static_cast<double>(successful_tests.size()) / results.size();
        
        std::cout << "\nTest success rate: " << std::fixed << std::setprecision(1) 
                  << (success_rate * 100) << "%" << std::endl;
    }
    
    void save_results(const std::vector<TestResult>& results) {
        std::ofstream file("large_file_cpp_test_results.json");
        if (!file.is_open()) {
            std::cout << "Warning: Could not save results to file" << std::endl;
            return;
        }
        
        file << "{\n";
        file << "  \"timestamp\": \"" << get_timestamp() << "\",\n";
        file << "  \"language\": \"cpp\",\n";
        file << "  \"test_results\": [\n";
        
        for (size_t i = 0; i < results.size(); ++i) {
            const auto& result = results[i];
            file << "    {\n";
            file << "      \"size_mb\": " << result.size_mb << ",\n";
            file << "      \"pattern\": \"" << result.pattern << "\",\n";
            file << "      \"compression_time_sec\": " << std::fixed << std::setprecision(6) 
                 << result.compression_time_sec << ",\n";
            file << "      \"decompression_time_sec\": " << std::fixed << std::setprecision(6) 
                 << result.decompression_time_sec << ",\n";
            file << "      \"compression_throughput_mb_s\": " << std::fixed << std::setprecision(2) 
                 << result.compression_throughput_mb_s << ",\n";
            file << "      \"decompression_throughput_mb_s\": " << std::fixed << std::setprecision(2) 
                 << result.decompression_throughput_mb_s << ",\n";
            file << "      \"compression_ratio\": " << std::fixed << std::setprecision(6) 
                 << result.compression_ratio << ",\n";
            file << "      \"compressed_size_mb\": " << std::fixed << std::setprecision(6) 
                 << result.compressed_size_mb << ",\n";
            file << "      \"bits_per_base\": " << std::fixed << std::setprecision(6) 
                 << result.bits_per_base << ",\n";
            file << "      \"integrity_verified\": " << (result.integrity_verified ? "true" : "false");
            
            if (!result.error_message.empty()) {
                file << ",\n      \"error\": \"" << result.error_message << "\"";
            }
            
            file << "\n    }";
            if (i < results.size() - 1) file << ",";
            file << "\n";
        }
        
        file << "  ],\n";
        
        // Calculate summary statistics
        std::vector<TestResult> successful_tests;
        for (const auto& result : results) {
            if (result.error_message.empty() && result.integrity_verified) {
                successful_tests.push_back(result);
            }
        }
        
        file << "  \"successful_tests\": " << successful_tests.size() << ",\n";
        file << "  \"total_tests\": " << results.size() << ",\n";
        file << "  \"success_rate\": " << std::fixed << std::setprecision(6) 
             << (results.empty() ? 0.0 : static_cast<double>(successful_tests.size()) / results.size()) << "\n";
        
        file << "}\n";
        file.close();
        
        std::cout << "\nDetailed results saved to: large_file_cpp_test_results.json" << std::endl;
    }
    
    std::string get_timestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::ostringstream oss;
        oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        return oss.str();
    }
};

int main() {
    std::cout << "CCC C++ Large File Performance Test" << std::endl;
    std::cout << "Warning: This test will consume significant memory and time." << std::endl;
    std::cout << "Testing files up to 100MB in size." << std::endl;
    std::cout << std::endl;
    
    std::cout << "Continue? (y/N): " << std::flush;
    std::string response;
    std::getline(std::cin, response);
    
    if (response != "y" && response != "Y") {
        std::cout << "Test cancelled." << std::endl;
        return 0;
    }
    
    try {
        LargeFileBenchmark benchmark;
        benchmark.run_all_tests();
        
        std::cout << "\n🎉 Large file performance test completed!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Test failed with exception: " << e.what() << std::endl;
        return 1;
    }
}
