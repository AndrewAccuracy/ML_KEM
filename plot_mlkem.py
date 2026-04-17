"""Plot benchmark results for ML-KEM parameter sets."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


FIGURES_DIR = Path("figures")
RESULTS_CSV = Path("results.csv")


def plot_timing(df: pd.DataFrame, column: str, error_column: str, title: str, output: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(df["algorithm"], df[column], yerr=df[error_column], capsize=5)
    plt.ylabel("Time (ms)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def plot_sizes(df: pd.DataFrame, output: Path) -> None:
    size_df = df[
        ["algorithm", "public_key_bytes", "secret_key_bytes", "ciphertext_bytes"]
    ].set_index("algorithm")
    size_df.plot(kind="bar", figsize=(10, 6))
    plt.ylabel("Bytes")
    plt.title("ML-KEM Size Overhead Comparison")
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def main() -> None:
    FIGURES_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(RESULTS_CSV)

    plot_timing(
        df,
        column="keygen_mean_ms",
        error_column="keygen_std_ms",
        title="ML-KEM KeyGen Average Time",
        output=FIGURES_DIR / "keygen_time.png",
    )
    plot_timing(
        df,
        column="encaps_mean_ms",
        error_column="encaps_std_ms",
        title="ML-KEM Encaps Average Time",
        output=FIGURES_DIR / "encaps_time.png",
    )
    plot_timing(
        df,
        column="decaps_mean_ms",
        error_column="decaps_std_ms",
        title="ML-KEM Decaps Average Time",
        output=FIGURES_DIR / "decaps_time.png",
    )
    plot_sizes(df, FIGURES_DIR / "size_overhead.png")

    print(f"Figures saved in {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
