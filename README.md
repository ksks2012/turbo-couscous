# Circular Chromosome Compression (CCC) Algorithm

## Algorithm Overview

Circular Chromosome Compression (CCC) is a bio-inspired data compression algorithm based on the chromosome structure of dinoflagellates. Dinoflagellate chromosomes are often circular, avoiding telomere issues of linear chromosomes, and use histone-free condensation for dense packing.

## Key Features

1. **Circular structure**: Mimics dinoflagellate circular chromosomes to eliminate boundary waste  
2. **DVNP compression**: Based on dinoflagellate viral nucleoprotein-like mechanisms  
3. **Trans-splicing markers**: Provide error detection and decoding guidance  
4. **DNA storage optimization**: Target compression of ~1.5–2 bits/base

## Installation and Setup

### Requirements
- Python 3.12+
- BioPython package
- Virtual environment (recommended)

### Installation steps
```bash
# Activate virtual environment
source rt-sandbox/bin/activate

# Install dependencies (already done)
pip install biopython numpy
```

## Usage

### Command-line interface

#### 1. Compress a file
```bash
python cmd/run.py compress input_file.txt output_file.ccc [options]

Options:
    --chunk-size INT       Chunk size for trans-splicing markers (default: 1000)
    --min-pattern INT      Minimum pattern length for DVNP compression (default: 4)
    --report               Generate compression report
    --export-dna           Export DNA sequence in FASTA format
```

#### 2. Decompress a file
```bash
python cmd/run.py decompress input_file.ccc output_file.txt [options]

Options:
    --verify               Verify file integrity
```

#### 3. Analyze file compressibility
```bash
python cmd/run.py analyze input_file.txt [options]
```

#### 4. Benchmark
```bash
python cmd/run.py benchmark [options]

Options:
    --test-sizes INT+      Test data sizes (bytes)
    --save-benchmark FILE  Save detailed results to a JSON file
```

### Python API

```python
from utils.circular_chromosome_compression import CircularChromosomeCompressor

# Initialize compressor
compressor = CircularChromosomeCompressor(
        chunk_size=1000,
        min_pattern_length=4
)

# Compress data
with open('input.txt', 'rb') as f:
        data = f.read()

compressed_data, metadata = compressor.compress(data)

# Decompress data
decompressed_data = compressor.decompress(compressed_data, metadata)

# Verify integrity
assert data == decompressed_data
```

## Algorithm Steps

### 1. Binary to DNA sequence
- Convert bytes to a binary string  
- Use 2-bit mapping: 00→A, 01→C, 10→G, 11→T  
- Produce a balanced nucleotide distribution

### 2. DVNP simulated compression
- Use an LZW variant algorithm  
- Detect and replace repeated patterns (similar to tandem repeats in dinoflagellates)  
- Dynamic dictionary management to simulate protein binding

### 3. Circular packaging
- Compute optimal circular length (prefer primes to avoid periodic artifacts)  
- Join head and tail to form a circle  
- Add bridging sequences to ensure circular integrity

### 4. Trans-splicing markers
- Simulate trans-splicing mechanisms  
- Embed markers for error detection and recovery  
- Include checksums and decoding guidance

## Performance Characteristics

### Compression notes
- Note: this algorithm is designed primarily for DNA storage systems, not general-purpose file compression  
- Includes DNA conversion overhead and bio-compatibility markers  
- Suited for long-term storage and biological integration

### Speed
- Compression speed: ~900–1000 KB/s  
- Decompression speed: ~1100–1500 KB/s  
- Memory usage: linear with input size

### DNA characteristics
- GC content: typically 50–60% (balanced distribution)  
- Sequence length: about 4× the original data (2 bits per base)  
- Synthesis cost: approximately $0.10 per base + fixed costs

## Use Cases

1. DNA data centers (e.g., Twist Bioscience systems)  
2. Space missions: long-term data storage  
3. Bio-computing: integration with biological systems  
4. Archival preservation: millennial-scale storage

## Repository Layout

```
├── cmd/
│   ├── __init__.py
│   └── run.py              # Command-line interface
├── utils/
│   ├── __init__.py
│   ├── circular_chromosome_compression.py  # Core algorithm
│   └── helpers.py          # Helper functions
├── test/
│   ├── __init__.py
│   └── test_ccc.py         # Test suite
├── rt-sandbox/             # Virtual environment
└── README.md
```

## Tests

```bash
# Run full test suite
python test/test_ccc.py

# Unit tests cover:
# - Binary/DNA conversion
# - DVNP compression/decompression
# - Circular packaging
# - Trans-splicing markers
# - End-to-end compression cycle
# - Integration scenarios
```

## Technical Details

### Theory
- Shannon information theory: theoretical limit ~2 bits/base  
- Circular hashing: avoids boundary effects  
- LZW compression: pattern detection and replacement  
- Error-correction codes: trans-splicing markers

### Biological inspiration
- Dinoflagellate circular chromosomes: no telomere issues  
- DVNP-like condensation: histone-free packing  
- Trans-splicing: mRNA quality control  
- High GC content: sequence stability

### Limitations and considerations
- Requires compute resources for conversion  
- Decompression simulates enzymatic processes  
- Compression ratio depends on data repetitiveness  
- Primarily intended for DNA storage, not general compression

## Example Results

```
=== Test file (805 bytes) ===
Compression time: 0.00 seconds
DNA sequence length: 3,220 bases
GC content: 58.54%
Estimated synthesis cost: $436.40
Integrity verification: ✓ Passed

=== Benchmark ===
1KB:  Compression 976 KB/s, Decompression 1513 KB/s
4KB:  Compression 1060 KB/s, Decompression 1146 KB/s  
16KB: Compression 913 KB/s, Decompression 1498 KB/s
```

## Future Work

1. Improve compression ratio: enhance DVNP algorithm  
2. Parallel processing: support multithreading  
3. Error correction: strengthen Reed–Solomon coding  
4. Biological validation: real DNA synthesis tests  
5. Standardization: integrate with DNA storage standards

---

# Note: 
This algorithm is developed for research and educational purposes to demonstrate bio-inspired data compression concepts. Real DNA storage applications require additional biological compatibility and stability considerations.
