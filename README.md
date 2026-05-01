# ML-KEM-512/768/1024 Performance Comparison and Security-Cost Analysis

This project benchmarks the three standardized ML-KEM parameter sets in `liboqs-python` and turns the raw results into a small research-style report. Instead of stopping at "which one is faster", the analysis is organized as:

- one main report
- three deeper analysis modules

The three modules are:

- normalized cost analysis
- full key-establishment cost analysis
- throughput / processing-capacity analysis

These metrics help explain the security-performance tradeoff among `ML-KEM-512`, `ML-KEM-768`, and `ML-KEM-1024`.

## Project Files

- `test_mlkem_basic.py`: correctness check for key generation, encapsulation, and decapsulation.
- `benchmark_mlkem.py`: runs repeated timing measurements and writes `results.csv`.
- `plot_mlkem.py`: reads `results.csv`, computes derived metrics, saves figures under `figures/`, and writes summary tables under `analysis/`.
- `results.csv`: benchmark output used throughout the report.

## Usage

```bash
python3 test_mlkem_basic.py
python3 benchmark_mlkem.py
python3 plot_mlkem.py
```

Generated outputs:

- `figures/keygen_time.png`
- `figures/encaps_time.png`
- `figures/decaps_time.png`
- `figures/size_overhead.png`
- `figures/normalized_costs.png`
- `figures/total_key_establishment_cost.png`
- `figures/throughput_comparison.png`
- `analysis/normalized_costs.csv`
- `analysis/total_costs.csv`
- `analysis/throughput.csv`

## Report Topic

Suggested title:

`ML-KEM-512/768/1024 的性能比较实验与安全代价分析`

Core research question:

Under the same experimental environment, how do the three standardized ML-KEM parameter sets differ in:

- time cost
- communication / storage cost
- full key-establishment cost
- throughput

And how much real overhead is introduced when the security level increases?

## Background

ML-KEM is the standardized key encapsulation mechanism defined in NIST FIPS 203. The standard specifies three parameter sets:

- `ML-KEM-512`
- `ML-KEM-768`
- `ML-KEM-1024`

These parameter sets are designed to provide increasing security strength at increasing performance cost. This project uses those three standard sets directly and compares them empirically.

## Experimental Setup

### Environment and Method

- Library: `liboqs-python`
- Algorithms: `ML-KEM-512`, `ML-KEM-768`, `ML-KEM-1024`
- Warmup rounds: `20`
- Measured rounds: `500`
- Measured operation: `KeyGen`
- Measured operation: `Encaps`
- Measured operation: `Decaps`
- Correctness check: verify that encapsulated and decapsulated shared secrets match

### Raw Benchmark Results

| Parameter Set | Security Level | Public Key (B) | Secret Key (B) | Ciphertext (B) | KeyGen (ms) | Encaps (ms) | Decaps (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ML-KEM-512 | 1 | 800 | 1632 | 768 | 0.008655 | 0.008859 | 0.009530 |
| ML-KEM-768 | 3 | 1184 | 2400 | 1088 | 0.014301 | 0.013227 | 0.014307 |
| ML-KEM-1024 | 5 | 1568 | 3168 | 1568 | 0.021371 | 0.019071 | 0.020608 |

The observed public-key, secret-key, and ciphertext lengths match the standardized ML-KEM parameter sizes, indicating that the implementation is using the standard parameter sets correctly.

## Module 1: Normalized Cost Analysis

### Goal

Absolute timing values alone do not immediately show how expensive a security upgrade is. To make the tradeoff clearer, this module treats `ML-KEM-512` as the baseline and normalizes all other costs against it.

### Formula

For any metric `X`:

```text
R_X(alg) = X(alg) / X(ML-KEM-512)
```

### Normalized Time Cost

| Metric | 512 | 768 | 1024 |
| --- | ---: | ---: | ---: |
| KeyGen | 1.00 | 1.65 | 2.47 |
| Encaps | 1.00 | 1.49 | 2.15 |
| Decaps | 1.00 | 1.50 | 2.16 |

### Normalized Size Cost

| Metric | 512 | 768 | 1024 |
| --- | ---: | ---: | ---: |
| Public key | 1.00 | 1.48 | 1.96 |
| Secret key | 1.00 | 1.47 | 1.94 |
| Ciphertext | 1.00 | 1.42 | 2.04 |

### Interpretation

- Moving from `ML-KEM-512` to `ML-KEM-768` raises most time costs to about `1.5x` and size costs to about `1.4x-1.5x`.
- Moving from `ML-KEM-512` to `ML-KEM-1024` raises time cost to about `2.1x-2.5x`, while key and ciphertext sizes are close to `2x`.
- This shows that higher security is not free; it introduces clear computation and communication overhead.

### Report Paragraph

Normalized analysis shows that upgrading from `ML-KEM-512` to `ML-KEM-768` increases runtime and data size to roughly `1.5x` of the baseline, while upgrading to `ML-KEM-1024` raises runtime to about `2.1x-2.5x` and nearly doubles the key and ciphertext sizes. Therefore, higher security strength in ML-KEM is accompanied by substantial time and communication overhead, which is consistent with the standardized security-performance tradeoff among the three parameter sets.

### PPT Title Suggestions

- `归一化代价分析：安全提升到底贵了多少？`
- `以 ML-KEM-512 为基准的相对开销比较`

## Module 2: Full Key-Establishment Cost Analysis

### Goal

Looking at `KeyGen`, `Encaps`, and `Decaps` separately is useful, but not always intuitive for deployment scenarios. This module combines them into workflow-level cost metrics.

### Definitions

Online key-establishment cost:

```text
T_online = T_Encaps + T_Decaps
```

Full key-establishment cost:

```text
T_full = T_KeyGen + T_Encaps + T_Decaps
```

### Total Cost Results

| Parameter Set | Encaps (ms) | Decaps (ms) | Online Total (ms) |
| --- | ---: | ---: | ---: |
| ML-KEM-512 | 0.008859 | 0.009530 | 0.018390 |
| ML-KEM-768 | 0.013227 | 0.014307 | 0.027534 |
| ML-KEM-1024 | 0.019071 | 0.020608 | 0.039678 |

| Parameter Set | KeyGen (ms) | Encaps (ms) | Decaps (ms) | Full Total (ms) |
| --- | ---: | ---: | ---: | ---: |
| ML-KEM-512 | 0.008655 | 0.008859 | 0.009530 | 0.027045 |
| ML-KEM-768 | 0.014301 | 0.013227 | 0.014307 | 0.041835 |
| ML-KEM-1024 | 0.021371 | 0.019071 | 0.020608 | 0.061050 |

### Normalized Total Cost

| Metric | 512 | 768 | 1024 |
| --- | ---: | ---: | ---: |
| Online total | 1.00 | 1.50 | 2.16 |
| Full total | 1.00 | 1.55 | 2.26 |

### Interpretation

- When viewed as a full KEM negotiation workflow, `ML-KEM-768` costs about `1.5x` of `ML-KEM-512`.
- `ML-KEM-1024` raises total cost to roughly `2.2x` of `ML-KEM-512`.
- This perspective is more useful for explaining real deployment cost than looking at a single primitive in isolation.
- `ML-KEM-768` shows a clear compromise profile: stronger than `512`, but not yet as expensive as `1024`.

### Report Paragraph

To better reflect practical deployment, this study defines both online key-establishment cost and full key-establishment cost. The online cost includes only encapsulation and decapsulation, while the full cost additionally includes key generation. Experimental results show that the online cost of `ML-KEM-768` is about `1.50x` that of `ML-KEM-512`, while `ML-KEM-1024` reaches `2.16x`. When key generation is included, the full cost rises to `1.55x` and `2.26x`, respectively. These results confirm that the overall computational cost of ML-KEM increases significantly with stronger parameter sets.

### PPT Title Suggestions

- `一次完整密钥建立要花多少代价？`
- `从单步操作到整体握手：ML-KEM 的总成本比较`

## Module 3: Throughput / Processing Capacity Analysis

### Goal

This module shifts the perspective from "how long one operation takes" to "how many operations can be completed per second".

### Formula

For any mean runtime in milliseconds:

```text
Throughput = 1000 / T_mean(ms)
```

Unit:

```text
ops/s
```

### Single-Operation Throughput

| Parameter Set | KeyGen (ops/s) | Encaps (ops/s) | Decaps (ops/s) |
| --- | ---: | ---: | ---: |
| ML-KEM-512 | 115544 | 112874 | 104927 |
| ML-KEM-768 | 69925 | 75603 | 69897 |
| ML-KEM-1024 | 46792 | 52436 | 48526 |

### Combined Throughput

| Parameter Set | Online Throughput (ops/s) | Full Throughput (ops/s) |
| --- | ---: | ---: |
| ML-KEM-512 | 54378 | 36976 |
| ML-KEM-768 | 36319 | 23903 |
| ML-KEM-1024 | 25203 | 16380 |

### Interpretation

- Larger parameter sets reduce the number of operations that can be completed per second.
- In the full key-establishment setting, `ML-KEM-512`, `ML-KEM-768`, and `ML-KEM-1024` achieve about `3.70e4`, `2.39e4`, and `1.64e4` operations per second, respectively.
- Higher security therefore not only slows each single operation, but also directly reduces overall system processing capacity.

### Report Paragraph

To study the impact of parameter choice on system capacity, the measured mean runtime is further converted into throughput in operations per second. The results show that `ML-KEM-512` provides the highest throughput for `KeyGen`, `Encaps`, and `Decaps`, while `ML-KEM-1024` is the slowest in all cases. For a full key-establishment workflow, the three parameter sets achieve approximately `36976`, `23903`, and `16380` operations per second, respectively. This indicates that stronger parameter sets not only increase per-operation cost, but also reduce the number of requests the system can process under high concurrency.

### PPT Title Suggestions

- `从时间到吞吐率：系统处理能力如何变化？`
- `更高安全参数会吞掉多少处理能力？`

## Suggested Full Report Structure

1. Introduction
2. Experimental design
3. Base benchmark results
4. Deep analysis I: normalized cost
5. Deep analysis II: full key-establishment cost
6. Deep analysis III: throughput
7. Discussion
8. Conclusion

### Suggested Discussion Points

- `ML-KEM-512`: lowest cost, strongest lightweight profile
- `ML-KEM-768`: balanced compromise between security and performance
- `ML-KEM-1024`: strongest security level but highest overhead
- parameter selection should depend on deployment scenario rather than a single metric

## Suggested 9-Slide PPT Structure

1. Research background
2. ML-KEM and research question
3. Experimental environment and method
4. Base result table and figures
5. Normalized cost analysis
6. Full key-establishment cost analysis
7. Throughput analysis
8. Overall discussion
9. Conclusion and limitations

## Short Conclusion

The three standardized ML-KEM parameter sets exhibit a clear hierarchy in both security level and performance cost. As the parameter set increases from `512` to `768` and `1024`, time overhead, data size, total key-establishment cost, and throughput loss all become more pronounced. Among the three, `ML-KEM-768` shows the clearest compromise profile in this experiment, offering stronger security than `ML-KEM-512` without incurring the full cost jump of `ML-KEM-1024`.
