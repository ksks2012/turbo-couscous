# Circular Chromosome Compression (CCC) - C++ Implementation

Bio-inspired compression algorithm based on dinoflagellate circular chromosomes and histone-free condensation mechanisms.

## Overview

This is a high-performance C++ implementation of the Circular Chromosome Compression algorithm that converts binary data to DNA sequences using circular structure to optimize storage density and enable efficient access patterns.

## Features

- **Bio-inspired Design**: Based on dinoflagellate chromosome structures
- **Binary-to-DNA Conversion**: 2-bit nucleotide encoding for balanced representation
- **DVNP-like Compression**: LZW-based compression with dynamic dictionary reset
- **Circular Encapsulation**: Eliminates boundary waste using prime-sized rings
- **Trans-splicing Markers**: Error correction and decoding guidance
- **Layered Architecture**: Modular design for core compression and encapsulation
- **Shannon Entropy Analysis**: Compression efficiency metrics
- **Hash-based Integrity**: Data verification during decompression
- **Large-scale Reliability**: Tested and verified on datasets up to 100MB+
- **Reset Marker Safety**: Fixed reset marker conflicts for 100% data integrity

## Algorithm Pipeline

1. **Binary Data → DNA Sequence** (2-bit encoding)
2. **DNA Sequence → DVNP Compression** (LZW-based)
3. **Compressed Data → Circular Encapsulation**
4. **Circular Data → Trans-splicing Markers**
5. **Hash-based Integrity Verification**

## Building with CMake

### Requirements
- CMake 3.16 or higher
- C++17 compatible compiler (GCC 7+ or Clang 5+)

### Quick Start

```bash
# Clone and build
cd cplusplus
./build.sh

# Or manual CMake build
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --parallel
```

### Build Options

The CMake build system supports several configuration options:

```bash
# Configure build options
cmake -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_TESTS=ON \
      -DBUILD_EXAMPLES=ON \
      -DBUILD_SHARED_LIBS=OFF \
      -DINSTALL_CCC=ON \
      ..
```

#### Available Options:
- `BUILD_TESTS` (ON/OFF) - Build test executables
- `BUILD_EXAMPLES` (ON/OFF) - Build example programs
- `BUILD_SHARED_LIBS` (ON/OFF) - Build shared libraries
- `INSTALL_CCC` (ON/OFF) - Enable installation
- `BUILD_DOCS` (ON/OFF) - Build documentation (requires Doxygen)

### Build Script Usage

The included `build.sh` script provides convenient build management:

```bash
# Basic usage
./build.sh                           # Release build
./build.sh --type Debug              # Debug build
./build.sh --clean                   # Clean build
./build.sh --clean --test --install  # Full build, test, and install

# All options
./build.sh --type Release \
           --dir build \
           --clean \
           --install \
           --test \
           --verbose
```

#### Script Options:
- `-t, --type TYPE` - Build type: Debug, Release (default: Release)
- `-d, --dir DIR` - Build directory (default: build)
- `-c, --clean` - Clean build directory before building
- `-i, --install` - Install after building
- `-T, --test` - Run tests after building
- `-v, --verbose` - Enable verbose output
- `-h, --help` - Show help message

## Usage

### Basic API Usage

```cpp
#include "circular_chromosome_compression.h"
using namespace ccc;

// Create compressor instance
CircularChromosomeCompressor compressor(
    1000,  // chunk_size for trans-splicing markers
    4,     // min_pattern_length for DVNP compression
    true,  // strict_mode (throw exceptions on errors)
    true   // verbose (enable debug output)
);

// Prepare data
std::string text = "Hello, World!";
std::vector<uint8_t> data(text.begin(), text.end());

// Compress
auto [compressed_data, metadata] = compressor.compress(data);

// Decompress
std::vector<uint8_t> decompressed = compressor.decompress(compressed_data, metadata);

// Get statistics
CompressionStats stats = compressor.get_compression_stats(data, compressed_data, metadata);
std::cout << "Compression ratio: " << stats.compression_ratio << std::endl;
```

### Running Examples and Tests

```bash
# Run comprehensive test suite
./build/test_ccc

# Run usage examples
./build/ccc_example

# Compress a specific file
./build/ccc_example filename.txt

# Run tests with CTest
cd build && ctest --output-on-failure
```

## Testing and Diagnostics

### Comprehensive Test Suite

The implementation includes extensive testing tools for validation:

```bash
# Basic functionality tests
./build/test_ccc

# Large-scale benchmark testing
./build/large_file_benchmark

# Reset marker integrity tests
./build/reset_analysis_test

# Mixed pattern diagnostics (previously problematic scenarios)
./build/exact_mixed_diagnostic

# Performance comparison with Python version
./benchmark_comparison.sh
```

### Diagnostic Tools

Several diagnostic executables are available for debugging:

- `reset_analysis_test` - Validates reset marker positioning
- `exact_mixed_diagnostic` - Tests mixed pattern integrity at various scales
- `failure_position_test` - Identifies precise failure locations in data
- `dict_exhaust_test` - Tests dictionary exhaustion scenarios
- `consecutive_reset_test` - Validates multiple consecutive resets

### Recent Improvements

**Reset Marker Fix (v1.1)**: Resolved "Invalid code after reset: 65535" error that affected mixed patterns at 20MB+ scale. The fix repositioned the reset marker to 65536 (outside the valid code range 0-65535) and implemented uint32_t internal handling for safe code space management.

## Installation

### System Installation

```bash
# Install to system directories (/usr/local by default)
./build.sh --install

# Or manually with CMake
cd build
sudo cmake --install .
```

### Custom Installation Path

```bash
# Install to custom location
mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/path/to/install ..
cmake --build . --parallel
cmake --install .
```

### Using Installed Library

After installation, you can use the library in your projects:

```cpp
// your_project.cpp
#include <circular_chromosome_compression.h>

int main() {
    ccc::CircularChromosomeCompressor compressor;
    // ... use the library
    return 0;
}
```

Compile with:
```bash
# Using pkg-config
g++ -std=c++17 $(pkg-config --cflags --libs ccc) your_project.cpp -o your_project

# Or manually
g++ -std=c++17 -lccc your_project.cpp -o your_project
```

## Project Structure

```
cplusplus/
├── CMakeLists.txt                      # Main CMake configuration
├── build.sh                           # Convenient build script
├── ccc.pc.in                         # pkg-config template
├── circular_chromosome_compression.h   # Header file
├── circular_chromosome_compression.cpp # Implementation
├── test_ccc_cpp.cpp                   # Test suite
├── example_usage.cpp                  # Usage examples
├── README.md                          # This file
└── build/                             # Build directory (created)
    ├── test_ccc                       # Test executable
    ├── ccc_example                    # Example executable
    ├── libccc.a                       # Static library
    └── ...                            # Other build artifacts
```

## CMake Targets

The build system creates several targets:

- `ccc_static` - Static library (libccc.a)
- `ccc_shared` - Shared library (libccc.so) [if BUILD_SHARED_LIBS=ON]
- `test_ccc` - Test executable
- `ccc_example` - Example executable
- `docs` - Documentation generation [if BUILD_DOCS=ON]

## Performance Characteristics

- **Small Text**: May expand due to overhead (metadata and markers)
- **Repetitive Data**: Excellent compression ratios via DVNP
- **Large Files**: Optimized with dynamic dictionary reset for sequences >1M bases
- **Mixed Patterns**: Full integrity maintained at 20MB+ scale (previously problematic)
- **Compression Speed**: 0.32-1.67 MB/s depending on data patterns
- **Decompression Speed**: 6.0-16.2 MB/s with hash verification
- **Reliability**: 100% success rate on comprehensive test suite (1MB-100MB)
- **Performance**: ~10-50x faster than Python implementation

## Development

### Debug Build

```bash
./build.sh --type Debug --clean --test --verbose
```

### Adding Custom Targets

You can extend the CMake configuration by adding custom targets:

```cmake
# Example: Add performance benchmark
add_executable(benchmark benchmark.cpp)
target_link_libraries(benchmark ccc_static)
```

### Code Coverage

For code coverage analysis with debug builds:

```bash
./build.sh --type Debug --clean
cd build
# Run tests with coverage
# Analyze coverage reports
```

## Integration Examples

### CMake Project Integration

```cmake
# In your CMakeLists.txt
find_package(PkgConfig REQUIRED)
pkg_check_modules(CCC REQUIRED ccc)

target_link_libraries(your_target ${CCC_LIBRARIES})
target_include_directories(your_target PRIVATE ${CCC_INCLUDE_DIRS})
target_compile_options(your_target PRIVATE ${CCC_CFLAGS_OTHER})
```

### Makefile Integration

```makefile
CXXFLAGS += $(shell pkg-config --cflags ccc)
LDFLAGS += $(shell pkg-config --libs ccc)

your_program: your_program.cpp
	$(CXX) $(CXXFLAGS) $< $(LDFLAGS) -o $@
```

## Troubleshooting

### Common Build Issues

1. **CMake version too old**: Upgrade to CMake 3.16+
2. **Compiler not found**: Install GCC 7+ or Clang 5+
3. **Missing C++17 support**: Update compiler or use older standard

### Runtime Issues

1. **Library not found**: Check `LD_LIBRARY_PATH` or install properly
2. **Header not found**: Verify installation or include path
3. **Linking errors**: Ensure proper library linking

## License

Same as the parent project.

## Contributing

When contributing to the C++ implementation:
1. Maintain compatibility with the Python API where possible
2. Follow C++17 standards and modern C++ practices
3. Include comprehensive tests for new features
4. Update CMake configuration for new components
5. Update documentation for API changes

## Comparison with Original Python Version

| Feature | C++ Version | Python Version |
|---------|-------------|----------------|
| Performance | ~10-50x faster | Baseline |
| Memory Usage | Lower overhead | Higher overhead |
| Dependencies | None (standard C++) | BioPython |
| Build System | CMake | setuptools |
| Package Manager | pkg-config | pip |
| Distribution | Binary/Source | Source only |
