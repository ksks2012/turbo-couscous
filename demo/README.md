# Demo Directory

This directory contains demonstration scripts for the Circular Chromosome Compression (CCC) algorithm.

## Main Demo Scripts

### Core Demonstrations
- **`comprehensive_demo.py`** - Complete CCC algorithm demonstration with multiple test cases
- **`genomic_compression_demo.py`** - Specialized genomic sequence compression with realistic biological patterns
- **`dictionary_reset_comprehensive.py`** - Comprehensive testing of dynamic dictionary reset functionality

### Analysis Demonstrations  
- **`shannon_analysis_demo.py`** - Shannon entropy analysis for compression optimization
- **`hash_verification_demo.py`** - Data integrity verification using cryptographic hashes

### Quick Tests
- **`quick_genomic_test.py`** - Fast validation of genomic compression patterns

## Backup Directories

### `demo_backup/`
Contains original test files that have been consolidated:
- `genomic_compression_test.py` → integrated into `genomic_compression_demo.py`
- `long_sequence_test.py` → integrated into `genomic_compression_demo.py`

### `bak/`
Contains archived development files:
- Performance optimization tests
- Debug utilities
- `reset_tests/` - Individual dictionary reset test files (now consolidated)

## Usage Examples

### Run Complete Genomic Demo
```bash
python demo/genomic_compression_demo.py
```

### Run Quick Test
```bash
python demo/quick_genomic_test.py
```

### Run Specific Pattern Test
```bash
python demo/genomic_compression_demo.py --pattern repetitive --size 50000
```

### Run Comprehensive Algorithm Demo
```bash
python demo/comprehensive_demo.py
```

### Run Dictionary Reset Tests
```bash
python demo/dictionary_reset_comprehensive.py
```

## Features Demonstrated

1. **Dynamic Dictionary Reset** - Automatic reset at 65,536 entries for long sequences
2. **Genomic Pattern Compression** - Realistic biological sequence patterns
3. **Scalability Testing** - Performance with large files (1MB-10MB)
4. **Data Integrity** - Cryptographic verification of compression/decompression
5. **Shannon Entropy Analysis** - Theoretical compression limits
6. **Error Handling** - Robust handling of edge cases

## File Organization

The demo directory has been cleaned up and organized:
- ✅ Duplicate files consolidated
- ✅ Empty files removed  
- ✅ Related functionality grouped together
- ✅ Clear naming conventions
- ✅ Backup copies preserved

All demonstration scripts use the main CCC algorithm implementation from `utils/circular_chromosome_compression.py`.
