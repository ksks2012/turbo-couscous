/**
 * Circular Chromosome Compression (CCC) Algorithm - C++ Implementation
 */

#include "circular_chromosome_compression.h"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <map>
#include <functional>

namespace ccc {

CircularChromosomeCompressor::CircularChromosomeCompressor(
    size_t chunk_size, 
    size_t min_pattern_length,
    bool strict_mode, 
    bool verbose
) : chunk_size_(chunk_size),
    min_pattern_length_(min_pattern_length),
    strict_mode_(strict_mode),
    verbose_(verbose),
    original_bits_length_(0) {
    
    // Initialize base mapping for DNA conversion
    base_mapping_["00"] = 'A';
    base_mapping_["01"] = 'C';
    base_mapping_["10"] = 'G';
    base_mapping_["11"] = 'T';
    
    reverse_mapping_['A'] = "00";
    reverse_mapping_['C'] = "01";
    reverse_mapping_['G'] = "10";
    reverse_mapping_['T'] = "11";
    
    // Fixed base dictionary for DVNP compression/decompression symmetry
    base_dict_[0] = 'A';
    base_dict_[1] = 'C';
    base_dict_[2] = 'G';
    base_dict_[3] = 'T';
}

void CircularChromosomeCompressor::log(const std::string& message) {
    if (verbose_) {
        std::cout << "[CCC] " << message << std::endl;
    }
}

bool CircularChromosomeCompressor::validate_input(const void* data, const std::string& data_name) {
    if (!data) {
        if (strict_mode_) {
            throw std::invalid_argument("Missing or empty " + data_name);
        } else {
            log("Warning: Missing or empty " + data_name + ", returning default");
            return false;
        }
    }
    return true;
}

double CircularChromosomeCompressor::calculate_entropy(const std::vector<uint8_t>& data) {
    if (data.empty()) {
        return 0.0;
    }
    
    // Count frequency of each byte value
    std::unordered_map<uint8_t, size_t> freq;
    for (uint8_t byte : data) {
        freq[byte]++;
    }
    
    size_t total = data.size();
    double entropy = 0.0;
    
    // Calculate Shannon entropy: H = -Σ(p * log2(p))
    for (const auto& pair : freq) {
        double probability = static_cast<double>(pair.second) / total;
        if (probability > 0) {
            entropy -= probability * std::log2(probability);
        }
    }
    
    log("Shannon entropy calculated: " + std::to_string(entropy) + " bits/byte");
    return entropy;
}

std::string CircularChromosomeCompressor::compute_data_hash(const std::vector<int>& data) {
    if (data.empty()) {
        return "";
    }
    
    std::ostringstream oss;
    for (size_t i = 0; i < data.size(); ++i) {
        if (i > 0) oss << ",";
        oss << data[i];
    }
    
    std::string data_str = oss.str();
    
    // Use std::hash as a simpler alternative to SHA-256
    std::hash<std::string> hasher;
    size_t hash_value = hasher(data_str);
    
    // Convert to hex string (first 8 characters)
    std::ostringstream hex_stream;
    hex_stream << std::hex << std::setfill('0') << std::setw(8) << (hash_value & 0xFFFFFFFF);
    
    return hex_stream.str();
}

bool CircularChromosomeCompressor::verify_data_integrity(
    const std::vector<int>& data, 
    const std::string& expected_hash, 
    const std::string& operation
) {
    if (expected_hash.empty()) {
        log("[CCC Warning] No hash available for " + operation + " integrity verification");
        return false;
    }
    
    std::string computed_hash = compute_data_hash(data);
    
    if (computed_hash == expected_hash) {
        log("[CCC Info] Data integrity verified successfully for " + operation);
        return true;
    } else {
        std::string error_msg = "Data integrity check failed during " + operation + 
                               ": hash mismatch (expected " + expected_hash + 
                               ", got " + computed_hash + ")";
        if (strict_mode_) {
            throw std::runtime_error(error_msg);
        } else {
            log("[CCC Warning] " + error_msg);
            if (verbose_) {
                std::cout << "[CCC Warning] " << error_msg << std::endl;
            }
            return false;
        }
    }
}

std::string CircularChromosomeCompressor::binary_to_dna(const std::vector<uint8_t>& binary_data) {
    if (binary_data.empty()) {
        if (!validate_input(nullptr, "binary_data")) {
            return "";
        }
    }
    
    log("Converting " + std::to_string(binary_data.size()) + " bytes to DNA sequence");
    
    // Convert bytes to binary string
    std::string bits;
    for (uint8_t byte : binary_data) {
        for (int i = 7; i >= 0; --i) {
            bits += ((byte >> i) & 1) ? '1' : '0';
        }
    }
    
    // Store original length for proper reconstruction
    original_bits_length_ = bits.length();
    
    // Pad if length is not even
    if (bits.length() % 2 != 0) {
        bits += '0';
    }
    
    // Convert to DNA sequence
    std::string dna_sequence;
    for (size_t i = 0; i < bits.length(); i += 2) {
        std::string two_bits = bits.substr(i, 2);
        dna_sequence += base_mapping_[two_bits];
    }
    
    log("Generated DNA sequence of length " + std::to_string(dna_sequence.length()));
    return dna_sequence;
}

std::vector<uint8_t> CircularChromosomeCompressor::dna_to_binary(const std::string& dna_seq) {
    if (dna_seq.empty()) {
        if (!validate_input(nullptr, "dna_seq")) {
            return {};
        }
    }
    
    log("Converting DNA sequence of length " + std::to_string(dna_seq.length()) + " back to binary");
    
    // Validate DNA sequence contains only valid bases
    std::string valid_dna = dna_seq;
    std::string filtered_dna;
    
    for (char base : dna_seq) {
        char upper_base = std::toupper(base);
        if (upper_base == 'A' || upper_base == 'C' || upper_base == 'G' || upper_base == 'T') {
            filtered_dna += upper_base;
        } else {
            if (strict_mode_) {
                throw std::invalid_argument("Invalid DNA base found: " + std::string(1, base));
            } else {
                log("Warning: Invalid DNA base " + std::string(1, base) + ", filtering it out");
            }
        }
    }
    
    // Convert DNA to binary string
    std::string bits;
    try {
        for (char base : filtered_dna) {
            bits += reverse_mapping_[base];
        }
    } catch (const std::exception& e) {
        if (strict_mode_) {
            throw std::invalid_argument("Invalid DNA base encountered");
        } else {
            log("Warning: Invalid DNA base encountered");
            return {};
        }
    }
    
    // Convert binary string to bytes
    std::vector<uint8_t> byte_array;
    for (size_t i = 0; i < bits.length(); i += 8) {
        std::string byte_chunk = bits.substr(i, std::min(size_t(8), bits.length() - i));
        if (byte_chunk.length() == 8) {
            byte_array.push_back(static_cast<uint8_t>(std::stoi(byte_chunk, nullptr, 2)));
        } else if (!byte_chunk.empty()) {
            // Handle incomplete byte by padding with zeros
            while (byte_chunk.length() < 8) {
                byte_chunk += '0';
            }
            byte_array.push_back(static_cast<uint8_t>(std::stoi(byte_chunk, nullptr, 2)));
        }
    }
    
    return byte_array;
}

bool CircularChromosomeCompressor::is_prime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    
    for (int i = 3; i <= std::sqrt(n); i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

int CircularChromosomeCompressor::next_prime(int n) {
    if (n < 2) return 2;
    
    while (!is_prime(n)) {
        n++;
    }
    return n;
}

std::vector<int> CircularChromosomeCompressor::dvnp_compress(const std::string& dna_seq) {
    if (dna_seq.empty()) {
        if (!validate_input(nullptr, "dna_seq")) {
            return {};
        }
    }
    
    log("Starting DVNP compression on sequence of length " + std::to_string(dna_seq.length()));
    
    // Initialize compression parameters
    std::unordered_map<std::string, int> dictionary;
    dictionary["A"] = 0;
    dictionary["C"] = 1;
    dictionary["G"] = 2;
    dictionary["T"] = 3;
    
    int next_code = 4;
    std::string current = "";
    std::vector<int> result;
    
    // Dynamic reset parameters for long sequences
    int reset_count = 0;
    const int max_dict_size = 65536;
    const int RESET_MARKER = 65535;
    
    log("Dynamic dictionary reset enabled for sequences >1M bases");
    
    // Main compression loop with dynamic dictionary reset
    for (char ch : dna_seq) {
        std::string combined = current + ch;
        
        if (dictionary.find(combined) != dictionary.end()) {
            current = combined;
        } else {
            if (!current.empty()) {
                result.push_back(dictionary[current]);
            }
            
            // Add new dictionary entry if space available
            if (next_code < max_dict_size) {
                dictionary[combined] = next_code;
                next_code++;
            } else {
                // Dictionary is full - implement dynamic reset
                result.push_back(RESET_MARKER);
                reset_count++;
                
                // Reset dictionary to initial state
                dictionary.clear();
                dictionary["A"] = 0;
                dictionary["C"] = 1;
                dictionary["G"] = 2;
                dictionary["T"] = 3;
                next_code = 4;
                
                log("Dictionary reset #" + std::to_string(reset_count) + 
                    " at position " + std::to_string(result.size() - 1));
            }
            current = std::string(1, ch);
        }
    }
    
    // Handle final sequence
    if (!current.empty()) {
        result.push_back(dictionary[current]);
    }
    
    double compression_ratio = static_cast<double>(result.size()) / dna_seq.length();
    log("DVNP compression completed: " + std::to_string(dna_seq.length()) + 
        " chars → " + std::to_string(result.size()) + " codes");
    log("Dictionary resets: " + std::to_string(reset_count) + 
        ", Final compression ratio: " + std::to_string(compression_ratio));
    
    return result;
}

std::string CircularChromosomeCompressor::dvnp_decompress(const std::vector<int>& compressed) {
    if (compressed.empty()) {
        if (!validate_input(nullptr, "compressed codes")) {
            return "";
        }
    }
    
    log("Starting DVNP decompression on " + std::to_string(compressed.size()) + " codes");
    
    // Initialize decompression parameters
    std::unordered_map<int, std::string> work_dict;
    for (const auto& pair : base_dict_) {
        work_dict[pair.first] = std::string(1, pair.second);
    }
    
    int next_code = 4;
    std::string result = "";
    int reset_count = 0;
    const int max_dict_size = 65536;
    const int RESET_MARKER = 65535;
    
    if (compressed.empty()) {
        return "";
    }
    
    // Handle first code
    if (compressed[0] == RESET_MARKER) {
        std::string error_msg = "First code cannot be a reset marker";
        if (strict_mode_) {
            throw std::invalid_argument(error_msg);
        } else {
            log("Warning: " + error_msg);
            return "";
        }
    }
    
    std::string prev = work_dict[compressed[0]];
    result = prev;
    
    // Process remaining codes with reset marker handling
    for (size_t i = 1; i < compressed.size(); ++i) {
        int code = compressed[i];
        
        // Check for dictionary reset marker
        if (code == RESET_MARKER) {
            reset_count++;
            log("Processing dictionary reset #" + std::to_string(reset_count));
            
            // Reset dictionary to initial state
            work_dict.clear();
            for (const auto& pair : base_dict_) {
                work_dict[pair.first] = std::string(1, pair.second);
            }
            next_code = 4;
            
            // Move to next code and start fresh
            i++;
            if (i >= compressed.size()) {
                break;
            }
            
            code = compressed[i];
            if (work_dict.find(code) != work_dict.end()) {
                prev = work_dict[code];
                result += prev;
                continue;
            } else {
                std::string error_msg = "Invalid code after reset: " + std::to_string(code);
                if (strict_mode_) {
                    throw std::invalid_argument(error_msg);
                } else {
                    log("Warning: " + error_msg);
                    break;
                }
            }
        }
        
        // Normal LZW decompression logic
        std::string entry;
        if (work_dict.find(code) != work_dict.end()) {
            entry = work_dict[code];
        } else if (code == next_code && !prev.empty()) {
            // Special case: code not in dictionary yet
            entry = prev + prev[0];
        } else {
            std::string error_msg = "Invalid code " + std::to_string(code) + 
                                  " in DVNP decompression (dict size: " + 
                                  std::to_string(work_dict.size()) + 
                                  ", next_code: " + std::to_string(next_code) + ")";
            if (strict_mode_) {
                throw std::invalid_argument(error_msg);
            } else {
                log("Warning: " + error_msg + ", skipping invalid code");
                continue;
            }
        }
        
        result += entry;
        
        // Add new dictionary entry if space available and prev is valid
        if (next_code < max_dict_size && !prev.empty() && !entry.empty()) {
            work_dict[next_code] = prev + entry[0];
            next_code++;
        }
        
        prev = entry;
    }
    
    log("DVNP decompression completed: " + std::to_string(compressed.size()) + 
        " codes → " + std::to_string(result.length()) + " chars");
    log("Dictionary resets processed: " + std::to_string(reset_count));
    
    return result;
}

std::vector<int> CircularChromosomeCompressor::circular_encapsulate(const std::vector<int>& compressed) {
    if (compressed.empty()) {
        return compressed;
    }
    
    size_t length = compressed.size();
    log("Starting circular encapsulation for " + std::to_string(length) + " codes");
    
    // Find next prime for optimal ring size to avoid periodic artifacts
    int prime_length = next_prime(static_cast<int>(length));
    size_t padding_size = prime_length - length;
    
    log("Circular padding size = " + std::to_string(padding_size) + 
        " (prime length: " + std::to_string(prime_length) + ")");
    
    // Pad with zeros if needed
    std::vector<int> padded = compressed;
    padded.resize(prime_length, 0);
    
    // Create bridge for circular continuity
    size_t bridge_length = std::min(static_cast<size_t>(std::sqrt(prime_length)), size_t(10));
    
    log("Bridge length = " + std::to_string(bridge_length));
    
    // Create circular structure
    std::vector<int> circular_ring = padded;
    for (size_t i = 0; i < bridge_length; ++i) {
        circular_ring.push_back(padded[i]);
    }
    
    log("Circular encapsulation completed: " + std::to_string(length) + 
        " → " + std::to_string(circular_ring.size()) + " codes");
    return circular_ring;
}

std::pair<std::vector<int>, TransSplicingMetadata> 
CircularChromosomeCompressor::add_trans_splicing_markers(
    const std::vector<int>& circular_data, 
    size_t original_compressed_length
) {
    if (circular_data.empty()) {
        TransSplicingMetadata metadata;
        metadata.sl_marker_code = 0;
        metadata.chunk_size = chunk_size_;
        metadata.original_length = 0;
        metadata.original_compressed_length = 0;
        return {std::vector<int>(), metadata};
    }
    
    // Generate spliced leader marker that doesn't conflict with data
    std::string data_hash = compute_data_hash(circular_data);
    
    // Find a marker code that doesn't exist in the data
    int max_value = *std::max_element(circular_data.begin(), circular_data.end());
    std::unordered_set<int> data_set(circular_data.begin(), circular_data.end());
    
    // Start with a value guaranteed to be outside the data range
    int sl_marker_code = max_value + 1;
    
    // Double-check it doesn't conflict
    while (data_set.find(sl_marker_code) != data_set.end()) {
        sl_marker_code++;
    }
    
    std::vector<int> marked_data;
    std::vector<size_t> marker_positions;
    
    // Insert markers at regular intervals
    for (size_t i = 0; i < circular_data.size(); i += chunk_size_) {
        // Add marker before chunk
        marked_data.push_back(sl_marker_code);
        marker_positions.push_back(marked_data.size() - 1);
        
        // Add chunk data
        size_t chunk_end = std::min(i + chunk_size_, circular_data.size());
        for (size_t j = i; j < chunk_end; ++j) {
            marked_data.push_back(circular_data[j]);
        }
    }
    
    // Metadata for decoding
    TransSplicingMetadata metadata;
    metadata.sl_marker_code = sl_marker_code;
    metadata.chunk_size = chunk_size_;
    metadata.original_length = circular_data.size();
    metadata.marker_positions = std::move(marker_positions);
    metadata.data_hash = data_hash;
    metadata.original_compressed_length = (original_compressed_length != 0) ? 
                                        original_compressed_length : circular_data.size();
    
    return {marked_data, metadata};
}

std::pair<std::vector<int>, CoreMetadata> 
CircularChromosomeCompressor::compress_core(const std::vector<uint8_t>& binary_data) {
    if (binary_data.empty()) {
        if (!validate_input(nullptr, "binary_data")) {
            CoreMetadata metadata;
            metadata.dna_length = 0;
            metadata.original_size = 0;
            metadata.original_bits_length = 0;
            return {std::vector<int>(), metadata};
        }
    }
    
    log("Starting core compression for " + std::to_string(binary_data.size()) + " bytes");
    
    // Step 1: Convert binary to DNA
    std::string dna_seq = binary_to_dna(binary_data);
    
    // Step 2: DVNP compression
    std::vector<int> compressed = dvnp_compress(dna_seq);
    
    // Core layer metadata
    CoreMetadata core_metadata;
    core_metadata.dna_length = dna_seq.length();
    core_metadata.original_size = binary_data.size();
    core_metadata.original_bits_length = original_bits_length_;
    
    return {compressed, core_metadata};
}

std::pair<std::vector<int>, EncapsulationMetadata> 
CircularChromosomeCompressor::encapsulate(const std::vector<int>& compressed) {
    if (compressed.empty()) {
        if (!validate_input(nullptr, "compressed data")) {
            EncapsulationMetadata metadata;
            metadata.circular_length = 0;
            return {std::vector<int>(), metadata};
        }
    }
    
    // Step 1: Circular encapsulation
    std::vector<int> circular_data = circular_encapsulate(compressed);
    
    // Step 2: Add trans-splicing markers
    auto [marked_data, ts_metadata] = add_trans_splicing_markers(circular_data, compressed.size());
    
    // Encapsulation layer metadata
    EncapsulationMetadata encap_metadata;
    encap_metadata.circular_length = circular_data.size();
    encap_metadata.trans_splicing = ts_metadata;
    
    return {marked_data, encap_metadata};
}

std::pair<std::vector<int>, CompressionMetadata> 
CircularChromosomeCompressor::compress(const std::vector<uint8_t>& binary_data) {
    if (binary_data.empty()) {
        if (!validate_input(nullptr, "binary_data")) {
            CompressionMetadata metadata;
            metadata.core.dna_length = 0;
            metadata.core.original_size = 0;
            metadata.core.original_bits_length = 0;
            metadata.encapsulation.circular_length = 0;
            metadata.compression_ratio = 0;
            return {std::vector<int>(), metadata};
        }
    }
    
    // Layer 1: Core compression
    auto [compressed, core_metadata] = compress_core(binary_data);
    
    // Layer 2: Encapsulation
    auto [final_data, encap_metadata] = encapsulate(compressed);
    
    // Combine metadata from all layers
    CompressionMetadata metadata;
    metadata.core = core_metadata;
    metadata.encapsulation = encap_metadata;
    metadata.compression_ratio = binary_data.empty() ? 0.0 : 
                               static_cast<double>(final_data.size()) / binary_data.size();
    
    return {final_data, metadata};
}

std::vector<int> CircularChromosomeCompressor::decapsulate(
    const std::vector<int>& marked_data, 
    const EncapsulationMetadata& encap_metadata
) {
    if (marked_data.empty() || encap_metadata.trans_splicing.sl_marker_code == 0) {
        return {};
    }
    
    // Step 1: Remove trans-splicing markers
    const TransSplicingMetadata& ts_metadata = encap_metadata.trans_splicing;
    int marker_code = ts_metadata.sl_marker_code;
    
    // Filter out markers
    std::vector<int> filtered_data;
    for (int x : marked_data) {
        if (x != marker_code) {
            filtered_data.push_back(x);
        }
    }
    
    // Step 2: Remove bridge elements and zero padding from circular encapsulation
    size_t original_length = ts_metadata.original_length;
    size_t original_compressed_length = ts_metadata.original_compressed_length;
    
    std::vector<int> core_data;
    if (original_length <= filtered_data.size()) {
        // Get the encapsulated data (without trans-splicing markers)
        std::vector<int> encapsulated_data(filtered_data.begin(), 
                                         filtered_data.begin() + original_length);
        
        // Step 3: Hash verification for data integrity
        std::string stored_hash = ts_metadata.data_hash;
        verify_data_integrity(encapsulated_data, stored_hash, "decapsulation");
        
        // Extract only the original compressed data, excluding zero padding and bridge elements
        size_t core_size = std::min(original_compressed_length, encapsulated_data.size());
        core_data.assign(encapsulated_data.begin(), encapsulated_data.begin() + core_size);
    } else {
        // Fallback - shouldn't happen in normal cases
        size_t core_size = std::min(original_compressed_length, filtered_data.size());
        core_data.assign(filtered_data.begin(), filtered_data.begin() + core_size);
        log("[CCC Warning] Data length inconsistency detected during decapsulation");
    }
    
    return core_data;
}

std::vector<uint8_t> CircularChromosomeCompressor::decompress_core(
    const std::vector<int>& compressed, 
    const CoreMetadata& core_metadata
) {
    if (compressed.empty()) {
        if (!validate_input(nullptr, "compressed codes") || 
            !validate_input(&core_metadata, "core_metadata")) {
            return {};
        }
    }
    
    log("Starting core decompression for " + std::to_string(compressed.size()) + " codes");
    
    // Step 1: DVNP decompression
    std::string dna_sequence = dvnp_decompress(compressed);
    
    // Step 2: Convert DNA back to binary
    std::vector<uint8_t> binary_data = dna_to_binary(dna_sequence);
    
    // Step 3: Ensure exact original length
    size_t expected_size = core_metadata.original_size;
    if (binary_data.size() > expected_size) {
        // Truncate extra bytes
        binary_data.resize(expected_size);
    } else if (binary_data.size() < expected_size) {
        // Pad with zeros if needed (this shouldn't normally happen)
        binary_data.resize(expected_size, 0);
    }
    
    return binary_data;
}

std::vector<uint8_t> CircularChromosomeCompressor::decompress(
    const std::vector<int>& compressed_data, 
    const CompressionMetadata& metadata
) {
    if (compressed_data.empty()) {
        if (!validate_input(nullptr, "compressed_data") || 
            !validate_input(&metadata, "metadata")) {
            return {};
        }
    }
    
    log("Starting decompression for " + std::to_string(compressed_data.size()) + " codes");
    
    // Layer 1: Decapsulation
    std::vector<int> core_data = decapsulate(compressed_data, metadata.encapsulation);
    
    // Layer 2: Core decompression
    std::vector<uint8_t> binary_data = decompress_core(core_data, metadata.core);
    
    return binary_data;
}

CompressionStats CircularChromosomeCompressor::get_compression_stats(
    const std::vector<uint8_t>& original_data,
    const std::vector<int>& compressed_data,
    const CompressionMetadata& /* metadata */
) {
    size_t original_size = original_data.size();
    
    // More accurate size calculation: determine bits needed per code
    size_t compressed_size = 0;
    size_t bits_per_code = 16; // minimum 16-bit
    
    if (!compressed_data.empty()) {
        int max_code = *std::max_element(compressed_data.begin(), compressed_data.end());
        bits_per_code = std::max(static_cast<size_t>(16), static_cast<size_t>((max_code > 0 ? 
                                 static_cast<int>(std::log2(max_code)) + 1 : 1) + 7) / 8 * 8);
        size_t compressed_size_bits = compressed_data.size() * bits_per_code;
        compressed_size = compressed_size_bits / 8;
    }
    
    // Calculate DNA sequence length for bits per base calculation
    size_t dna_length = original_size * 4; // 2 bits per base -> 4 bases per byte
    
    // Calculate Shannon entropy and efficiency metrics
    double original_entropy = calculate_entropy(original_data);
    
    // For compressed entropy, handle integer codes properly
    double compressed_entropy = 0.0;
    if (!compressed_data.empty()) {
        // Convert integer codes to bytes representation for entropy calculation
        std::vector<uint8_t> compressed_bytes;
        for (int code : compressed_data) {
            // Convert each code to bytes (using little-endian encoding)
            size_t num_bytes = (code > 0 ? (static_cast<size_t>(std::log2(code)) + 1 + 7) / 8 : 1);
            for (size_t i = 0; i < num_bytes; ++i) {
                compressed_bytes.push_back(static_cast<uint8_t>((code >> (i * 8)) & 0xFF));
            }
        }
        compressed_entropy = calculate_entropy(compressed_bytes);
    }
    
    double entropy_reduction = original_entropy - compressed_entropy;
    double theoretical_min_size = (original_size > 0) ? (original_entropy * original_size) / 8 : 0;
    
    // Compression effectiveness calculations
    double actual_ratio = (original_size > 0) ? static_cast<double>(compressed_size) / original_size : 0;
    double shannon_ratio = (original_size > 0) ? theoretical_min_size / original_size : 0;
    
    double shannon_efficiency = (compressed_size > 0) ? theoretical_min_size / compressed_size : 0;
    shannon_efficiency = std::min(1.0, shannon_efficiency); // Cap at 1.0
    
    double compression_effectiveness = 0.0;
    if (shannon_ratio > 0 && actual_ratio > shannon_ratio) {
        compression_effectiveness = shannon_ratio / actual_ratio;
    } else if (shannon_ratio > 0 && actual_ratio <= shannon_ratio) {
        compression_effectiveness = 1.0;
    }
    compression_effectiveness = std::min(1.0, std::max(0.0, compression_effectiveness));
    
    CompressionStats stats;
    stats.original_size_bytes = original_size;
    stats.compressed_size_bytes = compressed_size;
    stats.compression_ratio = actual_ratio;
    stats.space_savings_percent = (original_size > 0) ? (1 - actual_ratio) * 100 : 0;
    stats.bits_per_base = (dna_length > 0) ? (compressed_size * 8.0) / dna_length : 0;
    stats.bits_per_code = bits_per_code;
    stats.total_codes = compressed_data.size();
    stats.max_code_value = compressed_data.empty() ? 0 : 
                          *std::max_element(compressed_data.begin(), compressed_data.end());
    stats.original_entropy = original_entropy;
    stats.compressed_entropy = compressed_entropy;
    stats.entropy_reduction = entropy_reduction;
    stats.theoretical_minimum_size = theoretical_min_size;
    stats.shannon_efficiency = shannon_efficiency;
    stats.compression_effectiveness = compression_effectiveness;
    
    return stats;
}

} // namespace ccc
