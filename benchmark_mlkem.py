"""Benchmark ML-KEM KeyGen, Encaps, and Decaps operations."""

from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path

import oqs


ALGORITHMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
SECURITY_LEVELS = {
    "ML-KEM-512": 1,
    "ML-KEM-768": 3,
    "ML-KEM-1024": 5,
}
WARMUP_ROUNDS = 20
TEST_ROUNDS = 500
OUTPUT_CSV = Path("results.csv")


def benchmark_keygen(algorithm: str, rounds: int) -> list[float]:
    times = []
    with oqs.KeyEncapsulation(algorithm) as kem:
        for _ in range(rounds):
            t0 = time.perf_counter()
            kem.generate_keypair()
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
    return times


def benchmark_encaps(algorithm: str, rounds: int) -> list[float]:
    times = []
    with oqs.KeyEncapsulation(algorithm) as kem:
        public_key = kem.generate_keypair()
        for _ in range(rounds):
            t0 = time.perf_counter()
            kem.encap_secret(public_key)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
    return times


def benchmark_decaps(algorithm: str, rounds: int) -> list[float]:
    times = []
    with oqs.KeyEncapsulation(algorithm) as kem:
        public_key = kem.generate_keypair()
        ciphertext, shared_secret_enc = kem.encap_secret(public_key)
        for _ in range(rounds):
            t0 = time.perf_counter()
            shared_secret_dec = kem.decap_secret(ciphertext)
            t1 = time.perf_counter()
            assert shared_secret_dec == shared_secret_enc
            times.append((t1 - t0) * 1000.0)
    return times


def summarize(times: list[float]) -> tuple[float, float]:
    mean = statistics.mean(times)
    stddev = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean, stddev


def warmup() -> None:
    for algorithm in ALGORITHMS:
        with oqs.KeyEncapsulation(algorithm) as kem:
            for _ in range(WARMUP_ROUNDS):
                public_key = kem.generate_keypair()
                ciphertext, shared_secret_enc = kem.encap_secret(public_key)
                shared_secret_dec = kem.decap_secret(ciphertext)
                assert shared_secret_enc == shared_secret_dec


def collect_size_metadata(algorithm: str) -> dict[str, int]:
    with oqs.KeyEncapsulation(algorithm) as kem:
        public_key = kem.generate_keypair()
        ciphertext, shared_secret = kem.encap_secret(public_key)
        return {
            "public_key_bytes": len(public_key),
            "secret_key_bytes": kem.details["length_secret_key"],
            "ciphertext_bytes": len(ciphertext),
            "shared_secret_bytes": len(shared_secret),
        }


def main() -> None:
    warmup()
    rows = []

    for algorithm in ALGORITHMS:
        print(f"Benchmarking {algorithm} ...")
        keygen_times = benchmark_keygen(algorithm, TEST_ROUNDS)
        encaps_times = benchmark_encaps(algorithm, TEST_ROUNDS)
        decaps_times = benchmark_decaps(algorithm, TEST_ROUNDS)
        sizes = collect_size_metadata(algorithm)

        keygen_mean, keygen_std = summarize(keygen_times)
        encaps_mean, encaps_std = summarize(encaps_times)
        decaps_mean, decaps_std = summarize(decaps_times)

        rows.append(
            {
                "algorithm": algorithm,
                "security_level": SECURITY_LEVELS[algorithm],
                **sizes,
                "keygen_mean_ms": keygen_mean,
                "keygen_std_ms": keygen_std,
                "encaps_mean_ms": encaps_mean,
                "encaps_std_ms": encaps_std,
                "decaps_mean_ms": decaps_mean,
                "decaps_std_ms": decaps_std,
                "rounds": TEST_ROUNDS,
            }
        )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Results written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
