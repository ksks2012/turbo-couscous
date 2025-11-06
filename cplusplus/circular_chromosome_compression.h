/**
 * Circular Chromosome Compression (CCC) Algorithm - C++ Implementation
 * Bio-inspired by dinoflagellate circular chromosomes and histone-free condensation.
 *
 * This algorithm converts binary data to DNA sequences using circular structure
 * to optimize storage density and enable efficient access patterns.
 */

#ifndef CIRCULAR_CHROMOSOME_COMPRESSION_H
#define CIRCULAR_CHROMOSOME_COMPRESSION_H

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include <memory>

namespace ccc {

/**
 * Metadata structure for compression layers
 */
struct CoreMetadata {
    size_t dna_length = 0;
    size_t original_size = 0;
    size_t original_bits_length = 0;
};

struct TransSplicingMetadata {
    int sl_marker_code = 0;
    size_t chunk_size = 0;
    size_t original_length = 0;
    size_t original_compressed_length = 0;
    std::vector<size_t> marker_positions;
    std::string data_hash;
};

struct EncapsulationMetadata {
    size_t circular_length = 0;
    TransSplicingMetadata trans_splicing;
};

struct CompressionMetadata {
    CoreMetadata core;
    EncapsulationMetadata encapsulation;
    double compression_ratio = 0.0;
};

struct CompressionStats {
    size_t original_size_bytes = 0;
    size_t compressed_size_bytes = 0;
    double compression_ratio = 0.0;
    double space_savings_percent = 0.0;
    double bits_per_base = 0.0;
    size_t bits_per_code = 0;
    size_t total_codes = 0;
    int max_code_value = 0;
    double original_entropy = 0.0;
    double compressed_entropy = 0.0;
    double entropy_reduction = 0.0;
    double theoretical_minimum_size = 0.0;
    double shannon_efficiency = 0.0;
    double compression_effectiveness = 0.0;
};

/**
 * Circular Chromosome Compression Algorithm Implementation
 * Inspired by dinoflagellate chromosomes with DVNP-like compression and trans-splicing.
 */
class CircularChromosomeCompressor {
public:
    /**
     * Constructor with configuration parameters
     * 
     * @param chunk_size Size of chunks for trans-splicing markers
     * @param min_pattern_length Minimum length for pattern detection in DVNP compression
     * @param strict_mode If true, throw exceptions for invalid inputs; if false, return defaults
     * @param verbose If true, print debugging information during processing
     */
    explicit CircularChromosomeCompressor(
        size_t chunk_size = 1000, 
        size_t min_pattern_length = 4,
        bool strict_mode = true, 
        bool verbose = false
    );

    /**
     * Convert binary data to DNA sequence using 2-bit to base mapping
     * Inspired by balanced nucleotide distribution in dinoflagellates
     * 
     * @param binary_data Input binary data
     * @return DNA sequence string
     */
    std::string binary_to_dna(const std::vector<uint8_t>& binary_data);

    /**
     * Convert DNA sequence back to binary data
     * 
     * @param dna_seq DNA sequence string
     * @return Original binary data
     */
    std::vector<uint8_t> dna_to_binary(const std::string& dna_seq);

    /**
     * DVNP-simulated compression using improved LZW-like algorithm
     * Inspired by dinoflagellate viral nucleoprotein condensation mechanisms
     * 
     * @param dna_seq Input DNA sequence string
     * @return Compressed sequence as vector of integers with reset markers
     */
    std::vector<int> dvnp_compress(const std::string& dna_seq);

    /**
     * Decompress the DVNP-compressed sequence using improved LZW decompression
     * Must match compression logic exactly for perfect reconstruction
     * 
     * @param compressed Vector of integer codes (may contain reset markers)
     * @return Decompressed DNA sequence string
     */
    std::string dvnp_decompress(const std::vector<int>& compressed);

    /**
     * Complete compression pipeline using layered architecture
     * 
     * @param binary_data Input binary data
     * @return Pair of compressed data and metadata
     */
    std::pair<std::vector<int>, CompressionMetadata> compress(const std::vector<uint8_t>& binary_data);

    /**
     * Complete decompression pipeline using layered architecture
     * 
     * @param compressed_data Compressed data from compress()
     * @param metadata Metadata from compress()
     * @return Original binary data
     */
    std::vector<uint8_t> decompress(const std::vector<int>& compressed_data, const CompressionMetadata& metadata);

    /**
     * Calculate compression statistics and efficiency metrics
     * 
     * @param original_data Original binary data
     * @param compressed_data Compressed data
     * @param metadata Compression metadata
     * @return Dictionary with compression statistics
     */
    CompressionStats get_compression_stats(
        const std::vector<uint8_t>& original_data,
        const std::vector<int>& compressed_data,
        const CompressionMetadata& metadata
    );

    /**
     * Calculate Shannon entropy of binary data
     * 
     * @param data Input binary data
     * @return Shannon entropy in bits per byte
     */
    double calculate_entropy(const std::vector<uint8_t>& data);

private:
    // Configuration parameters
    size_t chunk_size_;
    size_t min_pattern_length_;
    bool strict_mode_;
    bool verbose_;
    size_t original_bits_length_;

    // Base mapping for DNA conversion
    std::unordered_map<std::string, char> base_mapping_;
    std::unordered_map<char, std::string> reverse_mapping_;
    std::unordered_map<int, char> base_dict_;

    // Private helper methods
    void log(const std::string& message);
    bool validate_input(const void* data, const std::string& data_name);
    
    std::string compute_data_hash(const std::vector<int>& data);
    bool verify_data_integrity(const std::vector<int>& data, const std::string& expected_hash, const std::string& operation = "decompression");
    
    bool is_prime(int n);
    int next_prime(int n);
    
    std::vector<int> circular_encapsulate(const std::vector<int>& compressed);
    std::pair<std::vector<int>, TransSplicingMetadata> add_trans_splicing_markers(
        const std::vector<int>& circular_data, 
        size_t original_compressed_length = 0
    );
    
    std::pair<std::vector<int>, CoreMetadata> compress_core(const std::vector<uint8_t>& binary_data);
    std::pair<std::vector<int>, EncapsulationMetadata> encapsulate(const std::vector<int>& compressed);
    
    std::vector<int> decapsulate(const std::vector<int>& marked_data, const EncapsulationMetadata& encap_metadata);
    std::vector<uint8_t> decompress_core(const std::vector<int>& compressed, const CoreMetadata& core_metadata);
};

} // namespace ccc

#endif // CIRCULAR_CHROMOSOME_COMPRESSION_H
