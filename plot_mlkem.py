"""Generate base and derived ML-KEM analysis figures from benchmark results."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
import pandas as pd


FIGURES_DIR = Path("figures")
ANALYSIS_DIR = Path("analysis")
RESULTS_CSV = Path("results.csv")
ALGORITHMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
TIME_COLUMNS = ["keygen_mean_ms", "encaps_mean_ms", "decaps_mean_ms"]
SIZE_COLUMNS = ["public_key_bytes", "secret_key_bytes", "ciphertext_bytes"]
BASELINE_ALGORITHM = "ML-KEM-512"
COLORS = ["#2A9D8F", "#E9C46A", "#E76F51"]
SCHEME_COLORS = {
    "ML-KEM-512": "#5B8E7D",
    "ML-KEM-768": "#B68A5A",
    "ML-KEM-1024": "#A56A63",
}
PAPER_BG = "#FCFCF8"
PAPER_HEADER = "#16324F"
PAPER_BORDER = "#D6DCE5"
PAPER_TEXT = "#1E2933"
ROW_STRIPE = "#F4F7FB"
HIGHLIGHT_LOW = "#DFF3EC"
HIGHLIGHT_HIGH = "#FDE9D9"
GRID_COLOR = "#D7DEE8"


plt.rcParams.update(
    {
        "figure.facecolor": PAPER_BG,
        "axes.facecolor": PAPER_BG,
        "savefig.facecolor": PAPER_BG,
        "font.family": "DejaVu Serif",
        "font.size": 11,
    }
)


def load_results() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_CSV)
    df["algorithm"] = pd.Categorical(df["algorithm"], categories=ALGORITHMS, ordered=True)
    return df.sort_values("algorithm").reset_index(drop=True)


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    derived = df.copy()

    derived["online_mean_ms"] = derived["encaps_mean_ms"] + derived["decaps_mean_ms"]
    derived["full_mean_ms"] = (
        derived["keygen_mean_ms"] + derived["encaps_mean_ms"] + derived["decaps_mean_ms"]
    )
    baseline = derived.loc[derived["algorithm"] == BASELINE_ALGORITHM].iloc[0]

    for column in TIME_COLUMNS + SIZE_COLUMNS + ["online_mean_ms", "full_mean_ms"]:
        normalized_name = f"{column}_norm"
        derived[normalized_name] = derived[column] / baseline[column]

    derived["keygen_throughput_ops_s"] = 1000.0 / derived["keygen_mean_ms"]
    derived["encaps_throughput_ops_s"] = 1000.0 / derived["encaps_mean_ms"]
    derived["decaps_throughput_ops_s"] = 1000.0 / derived["decaps_mean_ms"]
    derived["online_throughput_ops_s"] = 1000.0 / derived["online_mean_ms"]
    derived["full_throughput_ops_s"] = 1000.0 / derived["full_mean_ms"]

    return derived


def save_analysis_tables(df: pd.DataFrame) -> None:
    ANALYSIS_DIR.mkdir(exist_ok=True)

    normalized = df[
        [
            "algorithm",
            "keygen_mean_ms_norm",
            "encaps_mean_ms_norm",
            "decaps_mean_ms_norm",
            "public_key_bytes_norm",
            "secret_key_bytes_norm",
            "ciphertext_bytes_norm",
            "online_mean_ms_norm",
            "full_mean_ms_norm",
        ]
    ].rename(
        columns={
            "keygen_mean_ms_norm": "keygen_norm",
            "encaps_mean_ms_norm": "encaps_norm",
            "decaps_mean_ms_norm": "decaps_norm",
            "public_key_bytes_norm": "public_key_norm",
            "secret_key_bytes_norm": "secret_key_norm",
            "ciphertext_bytes_norm": "ciphertext_norm",
            "online_mean_ms_norm": "online_total_norm",
            "full_mean_ms_norm": "full_total_norm",
        }
    )
    normalized.to_csv(ANALYSIS_DIR / "normalized_costs.csv", index=False)

    totals = df[
        ["algorithm", "online_mean_ms", "full_mean_ms"]
    ].rename(
        columns={
            "online_mean_ms": "online_total_ms",
            "full_mean_ms": "full_total_ms",
        }
    )
    totals.to_csv(ANALYSIS_DIR / "total_costs.csv", index=False)

    throughput = df[
        [
            "algorithm",
            "keygen_throughput_ops_s",
            "encaps_throughput_ops_s",
            "decaps_throughput_ops_s",
            "online_throughput_ops_s",
            "full_throughput_ops_s",
        ]
    ].rename(
        columns={
            "keygen_throughput_ops_s": "keygen_ops_s",
            "encaps_throughput_ops_s": "encaps_ops_s",
            "decaps_throughput_ops_s": "decaps_ops_s",
            "online_throughput_ops_s": "online_ops_s",
            "full_throughput_ops_s": "full_ops_s",
        }
    )
    throughput.to_csv(ANALYSIS_DIR / "throughput.csv", index=False)


def plot_timing(df: pd.DataFrame, column: str, error_column: str, title: str, output: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(df["algorithm"], df[column], yerr=df[error_column], capsize=5, color=COLORS)
    plt.ylabel("Time (ms)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output, dpi=220)
    plt.close()


def plot_sizes(df: pd.DataFrame, output: Path) -> None:
    size_df = df[["algorithm", *SIZE_COLUMNS]].set_index("algorithm")
    ax = size_df.plot(kind="bar", figsize=(10, 6), color=["#2A9D8F", "#E9C46A", "#E76F51"])
    ax.set_ylabel("Bytes")
    ax.set_title("ML-KEM Size Overhead Comparison")
    plt.tight_layout()
    plt.savefig(output, dpi=220)
    plt.close()


def plot_normalized_costs(df: pd.DataFrame, output: Path) -> None:
    normalized = pd.DataFrame(
        {
            "algorithm": df["algorithm"],
            "KeyGen": df["keygen_mean_ms_norm"],
            "Encaps": df["encaps_mean_ms_norm"],
            "Decaps": df["decaps_mean_ms_norm"],
            "Public Key": df["public_key_bytes_norm"],
            "Secret Key": df["secret_key_bytes_norm"],
            "Ciphertext": df["ciphertext_bytes_norm"],
        }
    ).set_index("algorithm")

    ax = normalized.plot(kind="bar", figsize=(12, 6))
    ax.set_ylabel(f"Relative Cost (baseline = {BASELINE_ALGORITHM})")
    ax.set_title("Normalized Time and Size Cost")
    ax.legend(ncol=3, frameon=False)
    plt.tight_layout()
    plt.savefig(output, dpi=220)
    plt.close()


def plot_total_costs(df: pd.DataFrame, output: Path) -> None:
    totals = pd.DataFrame(
        {
            "algorithm": df["algorithm"],
            "Online Total": df["online_mean_ms"],
            "Full Total": df["full_mean_ms"],
        }
    ).set_index("algorithm")

    ax = totals.plot(kind="bar", figsize=(9, 5), color=["#2A9D8F", "#E76F51"])
    ax.set_ylabel("Time (ms)")
    ax.set_title("Total Cost per Key Establishment")
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(output, dpi=220)
    plt.close()


def plot_throughput(df: pd.DataFrame, output: Path) -> None:
    throughput = pd.DataFrame(
        {
            "algorithm": df["algorithm"],
            "KeyGen": df["keygen_throughput_ops_s"],
            "Encaps": df["encaps_throughput_ops_s"],
            "Decaps": df["decaps_throughput_ops_s"],
            "Online": df["online_throughput_ops_s"],
            "Full": df["full_throughput_ops_s"],
        }
    ).set_index("algorithm")

    ax = throughput.plot(kind="bar", figsize=(12, 6))
    ax.set_ylabel("Throughput (ops/s)")
    ax.set_title("ML-KEM Throughput Comparison")
    ax.legend(ncol=3, frameon=False)
    plt.tight_layout()
    plt.savefig(output, dpi=220)
    plt.close()


def style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor(PAPER_BG)
    ax.grid(True, axis="y", linestyle=(0, (3, 4)), color=GRID_COLOR, linewidth=0.8, alpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#B8C3D1")
    ax.spines["bottom"].set_color("#B8C3D1")
    ax.tick_params(colors="#44515F")


def blend_with_white(color: str, alpha: float) -> tuple[float, float, float]:
    rgb = np.array(mcolors.to_rgb(color))
    return tuple((1 - alpha) * np.ones(3) + alpha * rgb)


def save_figure(fig: plt.Figure, output: Path) -> None:
    fig.savefig(output, dpi=320, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def draw_horizontal_rule(fig: plt.Figure, y: float, color: str, linewidth: float) -> None:
    fig.add_artist(
        Line2D([0.03, 0.97], [y, y], transform=fig.transFigure, color=color, linewidth=linewidth)
    )


def render_paper_table(
    df: pd.DataFrame,
    title: str,
    subtitle: str,
    output: Path,
    formatters: dict[str, str],
    goal_by_column: dict[str, str],
) -> None:
    table_df = df.copy()
    display_df = table_df.copy()

    for column, fmt in formatters.items():
        if column in display_df.columns:
            display_df[column] = display_df[column].map(lambda value: fmt.format(value))

    rows = display_df.values.tolist()
    columns = display_df.columns.tolist()
    n_rows, n_cols = display_df.shape

    fig_height = 1.55 + 0.58 * (n_rows + 1)
    fig_width = max(7.4, 1.8 + 1.5 * n_cols)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    content_lengths = []
    for column in columns:
        column_values = [str(column)] + [str(value) for value in display_df[column].tolist()]
        content_lengths.append(max(len(value) for value in column_values) + 3)
    total_length = sum(content_lengths)
    col_widths = [length / total_length for length in content_lengths]
    if n_cols >= 3 and col_widths[0] < 0.18:
        remainder = 1.0 - 0.18
        other_total = sum(col_widths[1:])
        col_widths = [0.18] + [width / other_total * remainder for width in col_widths[1:]]
    table = ax.table(
        cellText=rows,
        colLabels=columns,
        colWidths=col_widths,
        cellLoc="center",
        colLoc="center",
        bbox=[0.02, 0.06, 0.96, 0.88],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.8 if n_cols >= 6 else 11.5)
    table.scale(1, 1.25)

    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(0.6)
        cell.set_edgecolor(PAPER_BORDER)
        cell.get_text().set_ha("center")
        cell.get_text().set_va("center")

        if row == 0:
            cell.set_facecolor(PAPER_HEADER)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
            cell.set_height(cell.get_height() * 1.08)
            continue

        base_color = "white" if row % 2 == 1 else ROW_STRIPE
        cell.set_facecolor(base_color)
        cell.get_text().set_color(PAPER_TEXT)

        if col == 0:
            cell.get_text().set_fontweight("bold")

    for col_idx, column_name in enumerate(table_df.columns[1:], start=1):
        numeric = pd.to_numeric(table_df[column_name], errors="coerce")
        if numeric.isna().all():
            continue

        goal = goal_by_column.get(column_name, "min")
        target_value = numeric.max() if goal == "max" else numeric.min()
        worst_value = numeric.min() if goal == "max" else numeric.max()
        span = worst_value - target_value

        for row_idx, value in enumerate(numeric.tolist(), start=1):
            cell = table[(row_idx, col_idx)]
            intensity = 0.0 if span == 0 else abs(value - worst_value) / abs(span)
            intensity = min(max(intensity, 0.0), 1.0)

            if abs(value - target_value) < 1e-12:
                accent = HIGHLIGHT_LOW if goal == "min" else HIGHLIGHT_HIGH
                cell.set_facecolor(accent)
                cell.get_text().set_fontweight("bold")
            elif intensity > 0.15:
                accent = HIGHLIGHT_LOW if goal == "min" else HIGHLIGHT_HIGH
                cell.set_facecolor(blend_with_white(accent, 0.18 + 0.22 * intensity))

    if title:
        fig.suptitle(title, fontsize=14, fontweight="bold", color=PAPER_TEXT, y=0.995)
    if subtitle:
        fig.text(0.5, 0.955, subtitle, fontsize=9.5, color="#54606C", ha="center", va="top")

    save_figure(fig, output)


def plot_paper_tables(df: pd.DataFrame) -> None:
    render_paper_table(
        df[
            [
                "algorithm",
                "keygen_mean_ms_norm",
                "encaps_mean_ms_norm",
                "decaps_mean_ms_norm",
                "online_mean_ms_norm",
                "full_mean_ms_norm",
            ]
        ].rename(
            columns={
                "algorithm": "Scheme",
                "keygen_mean_ms_norm": "KeyGen x",
                "encaps_mean_ms_norm": "Encaps x",
                "decaps_mean_ms_norm": "Decaps x",
                "online_mean_ms_norm": "Online x",
                "full_mean_ms_norm": "Full x",
            }
        ),
        title="",
        subtitle="",
        output=FIGURES_DIR / "paper_table_normalized_costs.png",
        formatters={
            "KeyGen x": "{:.2f}",
            "Encaps x": "{:.2f}",
            "Decaps x": "{:.2f}",
            "Online x": "{:.2f}",
            "Full x": "{:.2f}",
        },
        goal_by_column={
            "KeyGen x": "min",
            "Encaps x": "min",
            "Decaps x": "min",
            "Online x": "min",
            "Full x": "min",
        },
    )

    render_paper_table(
        df[["algorithm", "online_mean_ms", "full_mean_ms"]].rename(
            columns={
                "algorithm": "Scheme",
                "online_mean_ms": "Online Total (ms)",
                "full_mean_ms": "Full Total (ms)",
            }
        ),
        title="",
        subtitle="",
        output=FIGURES_DIR / "paper_table_total_costs.png",
        formatters={
            "Online Total (ms)": "{:.4f}",
            "Full Total (ms)": "{:.4f}",
        },
        goal_by_column={
            "Online Total (ms)": "min",
            "Full Total (ms)": "min",
        },
    )

    render_paper_table(
        df[
            [
                "algorithm",
                "keygen_throughput_ops_s",
                "encaps_throughput_ops_s",
                "decaps_throughput_ops_s",
                "online_throughput_ops_s",
                "full_throughput_ops_s",
            ]
        ].rename(
            columns={
                "algorithm": "Scheme",
                "keygen_throughput_ops_s": "KeyGen (ops/s)",
                "encaps_throughput_ops_s": "Encaps (ops/s)",
                "decaps_throughput_ops_s": "Decaps (ops/s)",
                "online_throughput_ops_s": "Online (ops/s)",
                "full_throughput_ops_s": "Full (ops/s)",
            }
        ),
        title="",
        subtitle="",
        output=FIGURES_DIR / "paper_table_throughput.png",
        formatters={
            "KeyGen (ops/s)": "{:,.0f}",
            "Encaps (ops/s)": "{:,.0f}",
            "Decaps (ops/s)": "{:,.0f}",
            "Online (ops/s)": "{:,.0f}",
            "Full (ops/s)": "{:,.0f}",
        },
        goal_by_column={
            "KeyGen (ops/s)": "max",
            "Encaps (ops/s)": "max",
            "Decaps (ops/s)": "max",
            "Online (ops/s)": "max",
            "Full (ops/s)": "max",
        },
    )


def plot_tradeoff_heatmap(df: pd.DataFrame, output: Path) -> None:
    metrics = pd.DataFrame(
        {
            "KeyGen": df["keygen_mean_ms_norm"].to_numpy(),
            "Encaps": df["encaps_mean_ms_norm"].to_numpy(),
            "Decaps": df["decaps_mean_ms_norm"].to_numpy(),
            "Online": df["online_mean_ms_norm"].to_numpy(),
            "Full": df["full_mean_ms_norm"].to_numpy(),
            "PubKey": df["public_key_bytes_norm"].to_numpy(),
            "Cipher": df["ciphertext_bytes_norm"].to_numpy(),
        },
        index=df["algorithm"].tolist(),
    )

    fig, ax = plt.subplots(figsize=(10.8, 4.9))
    fig.subplots_adjust(top=0.94, left=0.13, right=0.93, bottom=0.16)
    im = ax.imshow(metrics.values, cmap="GnBu", aspect="auto", vmin=1.0, vmax=metrics.values.max())

    ax.set_xticks(np.arange(metrics.shape[1]))
    ax.set_xticklabels(metrics.columns, fontsize=11, fontweight="bold")
    ax.set_yticks(np.arange(metrics.shape[0]))
    ax.set_yticklabels(metrics.index, fontsize=13, fontweight="bold")
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True, length=0)

    for i in range(metrics.shape[0] + 1):
        ax.axhline(i - 0.5, color="white", linewidth=2)
    for j in range(metrics.shape[1] + 1):
        ax.axvline(j - 0.5, color="white", linewidth=2)

    for row in range(metrics.shape[0]):
        for col in range(metrics.shape[1]):
            value = metrics.iloc[row, col]
            text = f"{value:.2f}x"
            weight = "bold" if abs(value - 1.0) < 1e-12 else "normal"
            color = "white" if value > metrics.values.mean() else PAPER_TEXT
            ax.text(col, row, text, ha="center", va="center", fontsize=11.5, color=color, fontweight=weight)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.ax.set_ylabel("Relative overhead", rotation=90, labelpad=12, color="#5B6774")
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(colors="#5B6774")

    save_figure(fig, output)


def plot_latency_dumbbell(df: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    fig.subplots_adjust(top=0.82, left=0.16, right=0.97, bottom=0.12)
    style_axes(ax)
    ax.grid(True, axis="x", linestyle=(0, (3, 4)), color=GRID_COLOR, linewidth=0.8, alpha=0.9)
    ax.grid(False, axis="y")

    y_positions = np.arange(len(df))[::-1]
    online = df["online_mean_ms"].to_numpy()
    full = df["full_mean_ms"].to_numpy()
    keygen = df["keygen_mean_ms"].to_numpy()

    ax.set_ylim(-0.12, len(df) - 1 + 0.58)

    for y, scheme, online_value, full_value, keygen_value in zip(y_positions, df["algorithm"], online, full, keygen):
        color = SCHEME_COLORS[scheme]
        ax.hlines(y, online_value, full_value, color=blend_with_white(color, 0.42), linewidth=8, zorder=1)
        ax.scatter(online_value, y, s=180, color=color, edgecolor="white", linewidth=1.6, zorder=3, marker="o")
        ax.scatter(full_value, y, s=210, color=blend_with_white(color, 0.62), edgecolor=color, linewidth=2.0, zorder=4, marker="D")
        online_offset = (4, 18) if y == y_positions.max() else (2, 12)
        full_offset = (-4, 18) if full_value == full.max() else (0, 12)
        ax.annotate(
            f"{online_value:.4f}",
            xy=(online_value, y),
            xytext=online_offset,
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=PAPER_TEXT,
        )
        ax.annotate(
            f"{full_value:.4f}",
            xy=(full_value, y),
            xytext=full_offset,
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=PAPER_TEXT,
        )
        ax.text(
            (online_value + full_value) / 2,
            y + 0.01,
            f"+{keygen_value:.4f} ms",
            ha="center",
            va="center",
            fontsize=9.2,
            color="#344454",
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": blend_with_white(color, 0.16), "edgecolor": "none"},
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(df["algorithm"], fontsize=13, fontweight="bold")
    ax.set_xlabel("Latency per key establishment (ms)", fontsize=12, color=PAPER_TEXT)
    fig.text(0.5, 0.955, "Online vs Full Latency", fontsize=17, fontweight="bold", color=PAPER_TEXT, ha="center")

    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#6787A8", markeredgecolor="white", markersize=10, label="Online"),
            Line2D([0], [0], marker="D", color="none", markerfacecolor="#DCE5EF", markeredgecolor="#6787A8", markersize=10, label="Full"),
        ],
        loc="upper right",
        frameon=False,
    )

    save_figure(fig, output)


def plot_pareto_bubble(df: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.8, 5.7))
    fig.subplots_adjust(top=0.84, left=0.12, right=0.97, bottom=0.12)
    style_axes(ax)
    ax.grid(True, axis="both", linestyle=(0, (3, 4)), color=GRID_COLOR, linewidth=0.8, alpha=0.9)

    x = df["full_mean_ms"].to_numpy()
    y = df["online_throughput_ops_s"].to_numpy()
    bubble_scale = 0.7
    ax.set_xlim(x.min() - 0.0015, x.max() + 0.0032)
    ax.set_ylim(20000, 60000)

    for _, row in df.iterrows():
        scheme = row["algorithm"]
        color = SCHEME_COLORS[scheme]
        ax.scatter(
            row["full_mean_ms"],
            row["online_throughput_ops_s"],
            s=(row["public_key_bytes"] + row["ciphertext_bytes"]) * bubble_scale,
            color=color,
            alpha=0.82,
            edgecolor="white",
            linewidth=2,
            zorder=3,
        )
        label_x = row["full_mean_ms"] + 0.00045
        label_y = row["online_throughput_ops_s"] + 450
        label_ha = "left"
        label_va = "bottom"
        if scheme == "ML-KEM-512":
            label_x = row["full_mean_ms"] + 0.00055
            label_y = row["online_throughput_ops_s"] - 2300
            label_va = "bottom"
        elif scheme == "ML-KEM-1024":
            label_x = row["full_mean_ms"] - 0.0024
            label_ha = "left"
            label_y = row["online_throughput_ops_s"] + 1000
        ax.text(
            label_x,
            label_y,
            f"{scheme}\nL{int(row['security_level'])}",
            fontsize=10,
            color=PAPER_TEXT,
            weight="bold",
            va=label_va,
            ha=label_ha,
        )

    ax.set_xlabel("Full latency (ms)  ↓", fontsize=12, color=PAPER_TEXT)
    ax.set_ylabel("Online throughput (ops/s)  ↑", fontsize=12, color=PAPER_TEXT)
    fig.text(0.5, 0.955, "Speed-Size-Security Tradeoff", fontsize=17, fontweight="bold", color=PAPER_TEXT, ha="center")

    bubble_examples = [1600, 2400, 3200]
    legend_handles = [
        ax.scatter([], [], s=value * bubble_scale, color="#BCC6D3", alpha=0.7, edgecolor="white", linewidth=1.5, label=f"{value} B")
        for value in bubble_examples
    ]
    legend = ax.legend(
        handles=legend_handles,
        title="PK + CT size",
        frameon=False,
        loc="upper right",
        bbox_to_anchor=(0.98, 0.98),
        borderaxespad=0.0,
        labelspacing=1.1,
        handletextpad=1.0,
        scatterpoints=1,
    )
    legend.get_title().set_color("#5B6774")

    save_figure(fig, output)


def plot_visual_storytelling(df: pd.DataFrame) -> None:
    plot_tradeoff_heatmap(df, FIGURES_DIR / "visual_heatmap_tradeoffs.png")
    plot_latency_dumbbell(df, FIGURES_DIR / "visual_latency_dumbbell.png")
    plot_pareto_bubble(df, FIGURES_DIR / "visual_pareto_bubble.png")


def main() -> None:
    FIGURES_DIR.mkdir(exist_ok=True)
    df = add_derived_metrics(load_results())
    save_analysis_tables(df)

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
    plot_normalized_costs(df, FIGURES_DIR / "normalized_costs.png")
    plot_total_costs(df, FIGURES_DIR / "total_key_establishment_cost.png")
    plot_throughput(df, FIGURES_DIR / "throughput_comparison.png")
    plot_paper_tables(df)
    plot_visual_storytelling(df)

    print(f"Figures saved in {FIGURES_DIR}/")
    print(f"Analysis tables saved in {ANALYSIS_DIR}/")


if __name__ == "__main__":
    main()
