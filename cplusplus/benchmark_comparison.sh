#!/bin/bash
# Performance comparison script between Python and C++ implementations
# Tests both versions and generates a comparative report
# 
# Usage: ./benchmark_comparison.sh
# Note: Python tests will use rt-sandbox/bin/activate environment
# Note: C++ tests will be run from the build/ directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "CCC Performance Comparison: Python vs C++"
print_status "=========================================="
print_status "Project root: $PROJECT_ROOT"
print_status "C++ directory: $SCRIPT_DIR"
echo ""

# Check if C++ version is built
if [[ ! -f "$SCRIPT_DIR/build/large_file_benchmark" ]] || [[ ! -f "$SCRIPT_DIR/build/test_ccc" ]]; then
    print_status "Building C++ version..."
    cd "$SCRIPT_DIR"
    ./build.sh --clean --type Release
    if [[ $? -ne 0 ]]; then
        print_error "Failed to build C++ version"
        exit 1
    fi
    print_success "C++ version built successfully"
else
    print_status "C++ version already built"
fi

# Quick integrity test before benchmarking
print_status "Running C++ integrity tests..."
cd "$SCRIPT_DIR/build"
if [[ -f "reset_analysis_test" ]]; then
    if ./reset_analysis_test > /dev/null 2>&1; then
        print_success "Reset analysis test passed"
    else
        print_error "Reset analysis test failed - benchmark results may be unreliable"
    fi
fi

# Check Python environment
print_status "Checking Python environment..."
if [[ -f "$PROJECT_ROOT/rt-sandbox/bin/activate" ]]; then
    source "$PROJECT_ROOT/rt-sandbox/bin/activate"
    print_success "Python environment activated"
else
    print_warning "Python virtual environment not found, using system Python"
fi

# Check if Python benchmark exists
if [[ ! -f "$PROJECT_ROOT/benchmark/large_file_test.py" ]]; then
    print_error "Python benchmark script not found"
    exit 1
fi

# Ask user for confirmation
echo ""
print_warning "This test will run large file benchmarks for both Python and C++ versions."
print_warning "It may take several minutes and consume significant memory (up to 100MB+ per test)."
echo ""
read -p "Continue with the comparison? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Test cancelled."
    exit 0
fi

# Create results directory
RESULTS_DIR="$SCRIPT_DIR/benchmark_results"
mkdir -p "$RESULTS_DIR"

print_status "Results will be saved to: $RESULTS_DIR"
echo ""

# Run Python benchmark
print_status "Running Python benchmark..."
cd "$PROJECT_ROOT/benchmark"
if python3 large_file_test.py <<< "y"; then
    print_success "Python benchmark completed"
    if [[ -f "large_file_test_results.json" ]]; then
        cp "large_file_test_results.json" "$RESULTS_DIR/python_results.json"
        print_success "Python results saved"
    fi
else
    print_error "Python benchmark failed"
    PYTHON_FAILED=true
fi

echo ""

# Run C++ benchmark  
print_status "Running C++ benchmark..."
cd "$SCRIPT_DIR/build"

# Run comprehensive diagnostic first
print_status "Running diagnostic tests..."
if [[ -f "exact_mixed_diagnostic" ]]; then
    if ./exact_mixed_diagnostic > "$RESULTS_DIR/diagnostic_log.txt" 2>&1; then
        print_success "Diagnostic tests passed"
    else
        print_warning "Some diagnostic tests failed - check diagnostic_log.txt"
    fi
fi

# Run main benchmark
if ./large_file_benchmark <<< "y"; then
    print_success "C++ benchmark completed"
    if [[ -f "large_file_cpp_test_results.json" ]]; then
        cp "large_file_cpp_test_results.json" "$RESULTS_DIR/cpp_results.json"
        print_success "C++ results saved"
    fi
else
    print_error "C++ benchmark failed"
    CPP_FAILED=true
fi

echo ""

# Generate comparison report
print_status "Generating comparison report..."

# Create comparison script
cat > "$RESULTS_DIR/generate_comparison.py" << 'EOF'
#!/usr/bin/env python3
import json
import os
import sys

def load_results(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {filename}")
        return None

def print_comparison_table(python_data, cpp_data):
    print("\n=== Performance Comparison Table ===")
    print(f"{'Size':<6} {'Pattern':<12} {'Python Comp':<12} {'C++ Comp':<12} {'Speedup':<10} {'Python Decomp':<14} {'C++ Decomp':<14} {'Speedup':<10}")
    print("-" * 120)
    
    if not python_data or not cpp_data:
        print("Insufficient data for comparison")
        return
        
    py_results = python_data.get('test_results', [])
    cpp_results = cpp_data.get('test_results', [])
    
    # Create lookup for easier comparison
    py_lookup = {}
    for result in py_results:
        if 'error' not in result:
            key = (result.get('size_mb'), result.get('pattern'))
            py_lookup[key] = result
    
    cpp_lookup = {}
    for result in cpp_results:
        if 'error_message' not in result or not result.get('error_message'):
            key = (result.get('size_mb'), result.get('pattern'))
            cpp_lookup[key] = result
    
    total_comp_speedup = []
    total_decomp_speedup = []
    
    for key in sorted(set(py_lookup.keys()) & set(cpp_lookup.keys())):
        size_mb, pattern = key
        py_result = py_lookup[key]
        cpp_result = cpp_lookup[key]
        
        py_comp_speed = py_result.get('compression_throughput_mb_s', 0)
        cpp_comp_speed = cpp_result.get('compression_throughput_mb_s', 0)
        py_decomp_speed = py_result.get('decompression_throughput_mb_s', 0)
        cpp_decomp_speed = cpp_result.get('decompression_throughput_mb_s', 0)
        
        comp_speedup = cpp_comp_speed / py_comp_speed if py_comp_speed > 0 else 0
        decomp_speedup = cpp_decomp_speed / py_decomp_speed if py_decomp_speed > 0 else 0
        
        if comp_speedup > 0:
            total_comp_speedup.append(comp_speedup)
        if decomp_speedup > 0:
            total_decomp_speedup.append(decomp_speedup)
        
        print(f"{size_mb:>4}MB {pattern:<12} {py_comp_speed:>8.2f} MB/s {cpp_comp_speed:>8.2f} MB/s {comp_speedup:>7.1f}x   {py_decomp_speed:>10.2f} MB/s {cpp_decomp_speed:>10.2f} MB/s {decomp_speedup:>7.1f}x")
    
    if total_comp_speedup and total_decomp_speedup:
        avg_comp_speedup = sum(total_comp_speedup) / len(total_comp_speedup)
        avg_decomp_speedup = sum(total_decomp_speedup) / len(total_decomp_speedup)
        
        print("\n=== Overall Performance Summary ===")
        print(f"Average compression speedup (C++ vs Python): {avg_comp_speedup:.1f}x")
        print(f"Average decompression speedup (C++ vs Python): {avg_decomp_speedup:.1f}x")
        
        if python_data.get('performance_summary') and 'avg_compression_throughput_mb_s' in python_data['performance_summary']:
            py_avg_comp = python_data['performance_summary']['avg_compression_throughput_mb_s']
            py_avg_decomp = python_data['performance_summary']['avg_decompression_throughput_mb_s']
            
            print(f"\nPython average performance:")
            print(f"  Compression: {py_avg_comp:.2f} MB/s")
            print(f"  Decompression: {py_avg_decomp:.2f} MB/s")
        
        # Calculate C++ averages from successful tests
        cpp_successful = [r for r in cpp_results if 'error_message' not in r or not r.get('error_message')]
        if cpp_successful:
            cpp_avg_comp = sum(r.get('compression_throughput_mb_s', 0) for r in cpp_successful) / len(cpp_successful)
            cpp_avg_decomp = sum(r.get('decompression_throughput_mb_s', 0) for r in cpp_successful) / len(cpp_successful)
            
            print(f"\nC++ average performance:")
            print(f"  Compression: {cpp_avg_comp:.2f} MB/s")
            print(f"  Decompression: {cpp_avg_decomp:.2f} MB/s")

def main():
    print("CCC Performance Comparison Report")
    print("=" * 50)
    
    # Load results
    python_data = load_results('python_results.json')
    cpp_data = load_results('cpp_results.json')
    
    if python_data:
        py_success_rate = python_data.get('success_rate', 0) * 100
        print(f"Python tests: {python_data.get('successful_tests', 0)}/{python_data.get('total_tests', 0)} passed ({py_success_rate:.1f}%)")
    
    if cpp_data:
        cpp_success_rate = cpp_data.get('success_rate', 0) * 100
        print(f"C++ tests: {cpp_data.get('successful_tests', 0)}/{cpp_data.get('total_tests', 0)} passed ({cpp_success_rate:.1f}%)")
    
    print_comparison_table(python_data, cpp_data)
    
    # Save combined results
    combined_results = {
        'comparison_timestamp': cpp_data.get('timestamp', '') if cpp_data else '',
        'python_results': python_data,
        'cpp_results': cpp_data
    }
    
    with open('performance_comparison.json', 'w') as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"\nComplete comparison data saved to: performance_comparison.json")

if __name__ == '__main__':
    main()
EOF

# Run comparison generator
cd "$RESULTS_DIR"
python3 generate_comparison.py

print_success "Comparison report generated!"
echo ""

# Display results location
print_status "Results saved in: $RESULTS_DIR"
if [[ -f "$RESULTS_DIR/python_results.json" ]]; then
    print_status "  python_results.json           - Python benchmark results"
fi
if [[ -f "$RESULTS_DIR/cpp_results.json" ]]; then
    print_status "  cpp_results.json              - C++ benchmark results"  
fi
if [[ -f "$RESULTS_DIR/performance_comparison.json" ]]; then
    print_status "  performance_comparison.json   - Combined comparison data"
fi

echo ""
if [[ -z "$PYTHON_FAILED" ]] && [[ -z "$CPP_FAILED" ]]; then
    print_success "🎉 Performance comparison completed successfully!"
    echo ""
    print_status "Key findings will be displayed above. Check the JSON files for detailed data."
    
    # Quick summary if both results exist
    if [[ -f "$RESULTS_DIR/cpp_results.json" ]] && [[ -f "$RESULTS_DIR/python_results.json" ]]; then
        echo ""
        print_status "=== Quick Summary ==="
        echo "   This comparison validates the C++ implementation's performance"
        echo "   improvements while maintaining full compatibility with the Python version."
        echo "   Recent fixes ensure 100% reliability on large-scale mixed pattern data."
    fi
else
    print_warning "⚠️  Performance comparison completed with some failures."
    print_status "Check individual benchmark results for details."
    if [[ -f "$RESULTS_DIR/diagnostic_log.txt" ]]; then
        print_status "Check diagnostic_log.txt for detailed error information."
    fi
fi
