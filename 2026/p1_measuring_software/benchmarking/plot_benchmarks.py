#!/usr/bin/env python3
"""Generate combined violin+box plots with Matplotlib for benchmark results."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "Matplotlib is required. Install with:\n"
        "  python3 -m pip install --user matplotlib\n"
        "or on Ubuntu/Debian:\n"
        "  sudo apt install python3-matplotlib"
    ) from exc


RESULT_FILE_RE = re.compile(r"^results_(nightly-\d{4}-\d{2}-\d{2})(?:_run(\d+))?$")
ENERGY_RE = re.compile(r"([0-9][0-9,]*\.[0-9]+)\s+Joules")
TIME_RE = re.compile(r"([0-9]+\.[0-9]+)\s+seconds time elapsed")


@dataclass(frozen=True)
class Sample:
    toolchain: str
    run_id: int
    energy_j: float
    time_s: float
    source_file: str


def parse_result_file(path: Path) -> Sample | None:
    match = RESULT_FILE_RE.match(path.name)
    if not match:
        return None

    toolchain = match.group(1)
    run_id = int(match.group(2)) if match.group(2) else 0

    text = path.read_text(encoding="utf-8", errors="replace")
    energy_match = ENERGY_RE.search(text)
    time_match = TIME_RE.search(text)
    if not energy_match or not time_match:
        return None

    return Sample(
        toolchain=toolchain,
        run_id=run_id,
        energy_j=float(energy_match.group(1).replace(",", "")),
        time_s=float(time_match.group(1)),
        source_file=path.name,
    )


def collect_samples(results_dir: Path) -> list[Sample]:
    samples: list[Sample] = []
    for path in sorted(results_dir.glob("results_nightly-*")):
        parsed = parse_result_file(path)
        if parsed is not None:
            samples.append(parsed)
    return samples


def sorted_toolchains(samples: list[Sample]) -> list[str]:
    return sorted({s.toolchain for s in samples}, key=lambda s: s.replace("nightly-", ""))


def grouped_metric(samples: list[Sample], toolchains: list[str], metric: str) -> list[list[float]]:
    grouped: list[list[float]] = []
    for tc in toolchains:
        vals = [getattr(s, metric) for s in samples if s.toolchain == tc]
        grouped.append(vals)
    return grouped


def write_csv(samples: list[Sample], out_csv: Path) -> None:
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["toolchain", "run_id", "energy_j", "time_s", "source_file"])
        for s in sorted(samples, key=lambda x: (x.toolchain, x.run_id, x.source_file)):
            writer.writerow([s.toolchain, s.run_id, f"{s.energy_j:.6f}", f"{s.time_s:.9f}", s.source_file])


def plot_violin_box(values: list[list[float]], labels: list[str], title: str, ylabel: str, out_file: Path) -> None:
    fig, ax = plt.subplots(figsize=(15, 6.5))
    positions = list(range(1, len(labels) + 1))

    vp = ax.violinplot(values, positions=positions, widths=0.9, showmeans=False, showmedians=False, showextrema=False)
    for body in vp["bodies"]:
        body.set_facecolor("#f4a261")
        body.set_edgecolor("#9c4f1f")
        body.set_alpha(0.45)

    bp = ax.boxplot(values, positions=positions, widths=0.35, patch_artist=True, showfliers=True)
    for box in bp["boxes"]:
        box.set_facecolor("#8ecae6")
        box.set_edgecolor("#1d4e89")
        box.set_alpha(0.95)
    for whisker in bp["whiskers"]:
        whisker.set_color("#264653")
    for cap in bp["caps"]:
        cap.set_color("#264653")
    for median in bp["medians"]:
        median.set_color("#111111")
        median.set_linewidth(2.0)
    for flier in bp["fliers"]:
        flier.set_marker(".")
        flier.set_alpha(0.5)
        flier.set_markerfacecolor("#444")

    ax.set_title(title)
    ax.set_xlabel("Rust nightly toolchain")
    ax.set_ylabel(ylabel)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def plot_energy_vs_time(
    energy_values: list[list[float]],
    time_values: list[list[float]],
    labels: list[str],
    out_file: Path,
) -> None:
    mean_energy = [sum(v) / len(v) for v in energy_values]
    mean_time = [sum(v) / len(v) for v in time_values]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(mean_time, mean_energy, s=70, c="#2a9d8f", edgecolors="#1b5e57", linewidths=0.8)

    for x, y, label in zip(mean_time, mean_energy, labels):
        ax.annotate(
            label,
            (x, y),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=8,
        )

    ax.set_title("Energy vs Runtime by Rust Nightly (Mean per Version)")
    ax.set_xlabel("Runtime (seconds)")
    ax.set_ylabel("Energy (Joules)")
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Matplotlib violin+box plots for benchmark results.")
    parser.add_argument("--results-dir", default="benchmarking/results")
    parser.add_argument("--out-dir", default="benchmarking/results/plots")
    parser.add_argument("--format", choices=["png", "svg", "pdf"], default="png")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    samples = collect_samples(results_dir)
    if not samples:
        raise SystemExit(f"No parseable result files found in: {results_dir}")

    write_csv(samples, out_dir / "benchmark_samples.csv")
    toolchains = sorted_toolchains(samples)
    energy_values = grouped_metric(samples, toolchains, "energy_j")
    time_values = grouped_metric(samples, toolchains, "time_s")

    plot_violin_box(
        energy_values,
        toolchains,
        "Energy by Rust Nightly (Violin + Box)",
        "Energy (Joules)",
        out_dir / f"energy_violin_box.{args.format}",
    )
    plot_violin_box(
        time_values,
        toolchains,
        "Runtime by Rust Nightly (Violin + Box)",
        "Time (seconds)",
        out_dir / f"time_violin_box.{args.format}",
    )
    plot_energy_vs_time(
        energy_values,
        time_values,
        toolchains,
        out_dir / f"energy_vs_time_versions.{args.format}",
    )

    print(f"Wrote {len(samples)} samples to {out_dir / 'benchmark_samples.csv'}")
    print(f"Wrote plots to {out_dir}")


if __name__ == "__main__":
    main()
