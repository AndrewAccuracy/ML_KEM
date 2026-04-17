# ML-KEM Benchmark

This directory contains a first-pass experiment scaffold for validating and benchmarking `ML-KEM-512`, `ML-KEM-768`, and `ML-KEM-1024` with `liboqs-python`.

## Files

- `test_mlkem_basic.py`: sanity-checks key generation, encapsulation, decapsulation, and shared-secret agreement.
- `benchmark_mlkem.py`: runs warmup plus repeated timing measurements for `KeyGen`, `Encaps`, and `Decaps`, then writes `results.csv`.
- `plot_mlkem.py`: reads `results.csv` and saves timing and size figures under `figures/`.

## Suggested setup

Install `liboqs` first, then install `liboqs-python`, and finally add plotting dependencies. A typical flow is:

```bash
git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python.git
cd liboqs-python
pip3 install .
cd ..
pip3 install pandas matplotlib
```

## Usage

```bash
python3 test_mlkem_basic.py
python3 benchmark_mlkem.py
python3 plot_mlkem.py
```

## Expected outputs

- `results.csv`
- `figures/keygen_time.png`
- `figures/encaps_time.png`
- `figures/decaps_time.png`
- `figures/size_overhead.png`
