#!/bin/bash
# Build script for Circular Chromosome Compression C++ library

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TYPE="Release"
BUILD_DIR=""
OUT_OF_SOURCE=false
CLEAN=false
INSTALL=false
RUN_TESTS=false
RUN_BENCHMARKS=false
NO_EXAMPLES=false
BUILD_EXAMPLES=true
CLEANUP_TEMP=false
VERBOSE=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE       Build type: Debug, Release (default: Release)"
    echo "  -d, --dir DIR         Build directory (default: . for in-source)"
    echo "  -o, --out-source      Use out-of-source build in ./build directory"
    echo "  -c, --clean           Clean build directory before building"
    echo "  -i, --install         Install after building"
    echo "  -T, --test            Run tests after building"
    echo "  -B, --benchmark       Run benchmarks after building"
    echo "  -E, --no-examples     Don't build examples"
    echo "  -C, --cleanup         Clean up temporary test files after build"
    echo "  -v, --verbose         Enable verbose output"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build with default settings"
    echo "  $0 -t Debug -c        # Clean debug build"
    echo "  $0 -c -T -B           # Clean, build, test, and benchmark"
    echo "  $0 -c -i -T -C        # Clean, build, install, test, and cleanup"
    echo "  $0 --type Release --clean --test --benchmark --verbose"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -d|--dir)
            BUILD_DIR="$2"
            shift 2
            ;;
        -o|--out-source)
            OUT_OF_SOURCE=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -T|--test)
            RUN_TESTS=true
            shift
            ;;
        -B|--benchmark)
            RUN_BENCHMARKS=true
            shift
            ;;
        -E|--no-examples)
            NO_EXAMPLES=true
            shift
            ;;
        -C|--cleanup)
            CLEANUP_TEMP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate build type
if [[ ! "$BUILD_TYPE" =~ ^(Debug|Release|RelWithDebInfo|MinSizeRel)$ ]]; then
    print_error "Invalid build type: $BUILD_TYPE"
    print_error "Valid types: Debug, Release, RelWithDebInfo, MinSizeRel"
    exit 1
fi

# Set up build directory
if [[ "$OUT_OF_SOURCE" == true ]]; then
    BUILD_DIR="build"
elif [[ -z "$BUILD_DIR" ]]; then
    BUILD_DIR="."
fi

# Set BUILD_EXAMPLES based on NO_EXAMPLES
if [[ "$NO_EXAMPLES" == true ]]; then
    BUILD_EXAMPLES=false
else
    BUILD_EXAMPLES=true
fi

print_status "Circular Chromosome Compression C++ Build Script"
print_status "================================================"
print_status "Build Type: $BUILD_TYPE"
print_status "Build Directory: $BUILD_DIR"
print_status "Out-of-source: $OUT_OF_SOURCE"
print_status "Clean: $CLEAN"
print_status "Install: $INSTALL"
print_status "Run Tests: $RUN_TESTS"
print_status "Run Benchmarks: $RUN_BENCHMARKS"
print_status "Build Examples: $BUILD_EXAMPLES"
print_status "Cleanup Temp Files: $CLEANUP_TEMP"
print_status "Verbose: $VERBOSE"
echo ""

# Check if CMake is available
if ! command -v cmake &> /dev/null; then
    print_error "CMake is not installed or not in PATH"
    exit 1
fi

# Check CMake version
CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
print_status "Using CMake version: $CMAKE_VERSION"

# Clean build directory if requested
if [[ "$CLEAN" == true ]]; then
    print_status "Cleaning build directory..."
    if [[ "$BUILD_DIR" == "." ]]; then
        # In-source build - clean specific files
        rm -f CMakeCache.txt
        rm -rf CMakeFiles/
        rm -f cmake_install.cmake
        rm -f Makefile
        rm -f *.a *.so *.dylib
        rm -f ccc_example test_ccc large_file_benchmark
        print_success "In-source build files cleaned"
    else
        # Out-of-source build - remove build directory and source dir cmake files
        if [[ -d "$BUILD_DIR" ]]; then
            rm -rf "$BUILD_DIR"
            print_success "Build directory cleaned"
        else
            print_warning "Build directory does not exist, nothing to clean"
        fi
        
        # Also clean any existing CMake files in source directory to ensure clean out-of-source build
        if [[ -f "CMakeCache.txt" ]] || [[ -d "CMakeFiles" ]]; then
            print_status "Cleaning existing CMake files from source directory for clean out-of-source build..."
            rm -f CMakeCache.txt
            rm -rf CMakeFiles/
            rm -f cmake_install.cmake
            rm -f Makefile
            rm -f *.a *.so *.dylib
            rm -f ccc_example test_ccc large_file_benchmark
            print_success "Source directory CMake files cleaned"
        fi
    fi
fi

# Set up build directory
if [[ "$BUILD_DIR" != "." ]]; then
    print_status "Creating build directory: $BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    SOURCE_DIR=".."
else
    print_status "Using in-source build"
    SOURCE_DIR="."
fi

# Configure with CMake
print_status "Configuring with CMake..."
CMAKE_ARGS=(
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
    -DBUILD_TESTS=ON
    -DBUILD_EXAMPLES="$BUILD_EXAMPLES"
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
)

if [[ "$VERBOSE" == true ]]; then
    CMAKE_ARGS+=(-DCMAKE_VERBOSE_MAKEFILE=ON)
fi

# Run cmake configuration
if [[ "$VERBOSE" == true ]]; then
    print_status "Current directory: $(pwd)"
    print_status "Source directory: $SOURCE_DIR"
    print_status "CMake command: cmake ${CMAKE_ARGS[*]} $SOURCE_DIR"
fi
cmake "${CMAKE_ARGS[@]}" "$SOURCE_DIR"

if [[ $? -ne 0 ]]; then
    print_error "CMake configuration failed"
    exit 1
fi

print_success "CMake configuration completed"

# Build
print_status "Building project..."
MAKE_ARGS=()

if [[ "$VERBOSE" == true ]]; then
    MAKE_ARGS+=(VERBOSE=1)
fi

# Determine number of parallel jobs
if command -v nproc &> /dev/null; then
    JOBS=$(nproc)
elif [[ -f /proc/cpuinfo ]]; then
    JOBS=$(grep -c ^processor /proc/cpuinfo)
else
    JOBS=2
fi

cmake --build . --parallel $JOBS

if [[ $? -ne 0 ]]; then
    print_error "Build failed"
    exit 1
fi

print_success "Build completed successfully"

# Run tests if requested
if [[ "$RUN_TESTS" == true ]]; then
    print_status "Running tests..."
    
    if [[ -f "./test_ccc" ]]; then
        ./test_ccc
        if [[ $? -eq 0 ]]; then
            print_success "All tests passed"
        else
            print_error "Some tests failed"
            exit 1
        fi
    else
        print_warning "Test executable not found, skipping tests"
    fi
    
    # Run CTest if available
    if command -v ctest &> /dev/null; then
        print_status "Running CTest..."
        ctest --output-on-failure
        if [[ $? -eq 0 ]]; then
            print_success "CTest completed successfully"
        else
            print_error "CTest failed"
            exit 1
        fi
    fi
fi

# Run benchmarks if requested
if [[ "$RUN_BENCHMARKS" == true ]]; then
    print_status "Running benchmarks..."
    
    if [[ -f "./large_file_benchmark" ]]; then
        print_status "Running large file benchmark (this may take a while)..."
        echo "y" | timeout 300 ./large_file_benchmark
        BENCHMARK_EXIT=$?
        
        if [[ $BENCHMARK_EXIT -eq 0 ]]; then
            print_success "Benchmarks completed successfully"
        elif [[ $BENCHMARK_EXIT -eq 124 ]]; then
            print_warning "Benchmark timed out (5 minutes limit)"
        else
            print_warning "Benchmarks completed with warnings (exit code: $BENCHMARK_EXIT)"
        fi
        
        if [[ -f "./large_file_cpp_test_results.json" ]]; then
            print_status "Benchmark results saved to: large_file_cpp_test_results.json"
        fi
    else
        print_warning "Benchmark executable not found, skipping benchmarks"
    fi
    
    # Run additional custom benchmarks if they exist
    for benchmark_exe in "./diagnostic_test" "./quick_20mb_test" "./final_validation_test"; do
        if [[ -f "$benchmark_exe" ]]; then
            print_status "Running $(basename "$benchmark_exe")..."
            $benchmark_exe
            if [[ $? -eq 0 ]]; then
                print_success "$(basename "$benchmark_exe") completed successfully"
            else
                print_warning "$(basename "$benchmark_exe") completed with warnings"
            fi
        fi
    done
fi

# Install if requested
if [[ "$INSTALL" == true ]]; then
    print_status "Installing..."
    
    # Check if we need sudo
    INSTALL_PREFIX=$(cmake -L . | grep CMAKE_INSTALL_PREFIX | cut -d'=' -f2)
    if [[ "$INSTALL_PREFIX" =~ ^/usr ]]; then
        if [[ $EUID -ne 0 ]]; then
            print_warning "Installation to system directory requires sudo"
            sudo cmake --install .
        else
            cmake --install .
        fi
    else
        cmake --install .
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "Installation completed"
        print_status "Installed to: $INSTALL_PREFIX"
    else
        print_error "Installation failed"
        exit 1
    fi
fi

# Cleanup temporary files if requested
if [[ "$CLEANUP_TEMP" == true ]]; then
    print_status "Cleaning up temporary files..."
    
    # Remove test executables that were created during development
    TEMP_FILES=(
        "./binary_dna_test"
        "./consecutive_reset_test" 
        "./debug_reset_test"
        "./diagnostic_test"
        "./dvnp_reset_test"
        "./exact_benchmark_test"
        "./pipeline_test"
        "./simple_dvnp_test"
        "./final_validation_test"
        "./test_edge_cases"
        "./test_reset_issue"
        "./reproduce_issue_20mb"
        "*.o"
        "*.tmp"
    )
    
    for file_pattern in "${TEMP_FILES[@]}"; do
        if ls $file_pattern 1> /dev/null 2>&1; then
            rm -f $file_pattern
            print_status "Removed: $file_pattern"
        fi
    done
    
    # Remove temporary test result files
    if [[ -f "./large_file_cpp_test_results.json" ]] && [[ "$RUN_BENCHMARKS" != true ]]; then
        print_status "Keeping benchmark results file (use -B to regenerate)"
    fi
    
    print_success "Cleanup completed"
fi

print_success "Build process completed successfully!"
print_status ""
print_status "Available executables in build directory:"
if [[ -f "./test_ccc" ]]; then
    print_status "  ./test_ccc               - Run comprehensive tests"
fi
if [[ -f "./ccc_example" ]]; then
    print_status "  ./ccc_example            - Run usage examples"
fi
if [[ -f "./large_file_benchmark" ]]; then
    print_status "  ./large_file_benchmark   - Run large file performance tests"
fi
if [[ -f "./libccc.a" ]]; then
    print_status "  ./libccc.a               - Static library"
fi

# Check for development test executables
DEV_EXECUTABLES=(
    "./diagnostic_test"
    "./quick_20mb_test"
    "./pipeline_test"
)

for exe in "${DEV_EXECUTABLES[@]}"; do
    if [[ -f "$exe" ]]; then
        print_status "  $exe        - Development test"
    fi
done

print_status ""
print_status "Build information:"
print_status "  Build directory: $BUILD_DIR"
print_status "  Build type: $BUILD_TYPE"
if [[ -f "./compile_commands.json" ]]; then
    print_status "  Compile commands: ./compile_commands.json (for IDEs/tools)"
fi

print_status ""
print_status "Quick commands:"
print_status "  Clean build: rm -rf $BUILD_DIR"
if [[ "$INSTALL" == false ]]; then
    print_status "  Install: $0 --install"
fi
print_status "  Test only: $0 --test"
print_status "  Benchmark: $0 --benchmark"
print_status "  Full cycle: $0 --clean --test --benchmark --cleanup"
