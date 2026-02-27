#!/usr/bin/env python3
"""Run ANOVA and regression analysis for benchmark results."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


RESULT_RE = re.compile(r"^results_(nightly-\d{4}-\d{2}-\d{2})_run(\d+)$")
ENERGY_RE = re.compile(r"([0-9][0-9,]*\.[0-9]+)\s+Joules")
TIME_RE = re.compile(r"([0-9]+\.[0-9]+)\s+seconds time elapsed")


@dataclass(frozen=True)
class Sample:
    toolchain: str
    run_id: int
    energy_j: float
    time_s: float


def parse_samples(results_dir: Path) -> list[Sample]:
    out: list[Sample] = []
    for p in sorted(results_dir.glob("results_nightly-*_run*")):
        m = RESULT_RE.match(p.name)
        if not m:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        em = ENERGY_RE.search(text)
        tm = TIME_RE.search(text)
        if not em or not tm:
            continue
        out.append(
            Sample(
                toolchain=m.group(1),
                run_id=int(m.group(2)),
                energy_j=float(em.group(1).replace(",", "")),
                time_s=float(tm.group(1)),
            )
        )
    return out


def eta_squared(groups: list[np.ndarray]) -> float:
    all_vals = np.concatenate(groups)
    grand_mean = np.mean(all_vals)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = sum(np.sum((g - grand_mean) ** 2) for g in groups)
    return float(ss_between / ss_total)


def write_tukey_csv(
    labels: list[str],
    tukey: stats._hypotests.TukeyHSDResult,  # type: ignore[attr-defined]
    out_csv: Path,
) -> None:
    ci = tukey.confidence_interval()
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["group_a", "group_b", "mean_diff", "p_value", "ci_low", "ci_high", "significant_0.05"])
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                mean_diff = float(tukey.statistic[i, j])
                p_val = float(tukey.pvalue[i, j])
                ci_low = float(ci.low[i, j])
                ci_high = float(ci.high[i, j])
                writer.writerow([labels[i], labels[j], f"{mean_diff:.6f}", f"{p_val:.6g}", f"{ci_low:.6f}", f"{ci_high:.6f}", p_val < 0.05])


def plot_regression(samples: list[Sample], out_png: Path) -> stats._stats_py.LinregressResult:  # type: ignore[attr-defined]
    x = np.array([s.time_s for s in samples], dtype=float)
    y = np.array([s.energy_j for s in samples], dtype=float)
    fit = stats.linregress(x, y)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x, y, s=18, alpha=0.35, color="#2a9d8f", edgecolors="none", label="Runs")

    xs = np.linspace(float(x.min()), float(x.max()), 200)
    ys = fit.intercept + fit.slope * xs
    ax.plot(xs, ys, color="#e76f51", linewidth=2.2, label="Linear fit")

    ax.set_title("Energy vs Time with Linear Regression (all runs)")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Energy (Joules)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="upper right")
    ax.text(
        0.02,
        0.98,
        f"energy = {fit.intercept:.2f} + {fit.slope:.2f} * time\nR^2 = {fit.rvalue**2:.4f}, p = {fit.pvalue:.3e}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9, "edgecolor": "#ccc"},
    )

    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    plt.close(fig)
    return fit


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ANOVA and regression on benchmark result files.")
    parser.add_argument("--results-dir", default="benchmarking/results")
    parser.add_argument("--out-dir", default="benchmarking/results/stats")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    samples = parse_samples(results_dir)
    if not samples:
        raise SystemExit(f"No parseable results found in {results_dir}")

    labels = sorted({s.toolchain for s in samples}, key=lambda s: s.replace("nightly-", ""))
    energy_groups = [np.array([s.energy_j for s in samples if s.toolchain == l], dtype=float) for l in labels]
    time_groups = [np.array([s.time_s for s in samples if s.toolchain == l], dtype=float) for l in labels]

    f_energy, p_energy = stats.f_oneway(*energy_groups)
    f_time, p_time = stats.f_oneway(*time_groups)
    eta_energy = eta_squared(energy_groups)
    eta_time = eta_squared(time_groups)

    tukey_energy = stats.tukey_hsd(*energy_groups)
    tukey_time = stats.tukey_hsd(*time_groups)

    write_tukey_csv(labels, tukey_energy, out_dir / "anova_tukey_energy.csv")
    write_tukey_csv(labels, tukey_time, out_dir / "anova_tukey_time.csv")

    fit = plot_regression(samples, out_dir / "energy_time_regression.png")

    df_between = len(labels) - 1
    df_within = len(samples) - len(labels)
    slope_ci_low = fit.slope - 1.96 * fit.stderr
    slope_ci_high = fit.slope + 1.96 * fit.stderr

    summary = out_dir / "stats_summary.md"
    summary.write_text(
        "\n".join(
            [
                "# Statistical analysis",
                "",
                f"- Runs used: **{len(samples)}**",
                f"- Toolchains: **{len(labels)}**",
                "",
                "## One-way ANOVA by toolchain",
                "",
                f"- Energy: `F({df_between}, {df_within}) = {f_energy:.2f}`, `p = {p_energy:.3e}`, eta^2 `= {eta_energy:.3f}`",
                f"- Time: `F({df_between}, {df_within}) = {f_time:.2f}`, `p = {p_time:.3e}`, eta^2 `= {eta_time:.3f}`",
                "",
                "## Linear regression (Energy vs Time, all runs)",
                "",
                f"- Model: `energy_J = {fit.intercept:.2f} + {fit.slope:.2f} * time_s`",
                f"- `R^2 = {fit.rvalue**2:.4f}`, `r = {fit.rvalue:.4f}`, `p = {fit.pvalue:.3e}`",
                f"- Slope 95% CI: `[{slope_ci_low:.2f}, {slope_ci_high:.2f}]` J/s",
                "",
                "## Outputs",
                "",
                "- `energy_time_regression.png`",
                "- `anova_tukey_energy.csv`",
                "- `anova_tukey_time.csv`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote: {summary}")
    print(f"Wrote: {out_dir / 'energy_time_regression.png'}")
    print(f"Wrote: {out_dir / 'anova_tukey_energy.csv'}")
    print(f"Wrote: {out_dir / 'anova_tukey_time.csv'}")


if __name__ == "__main__":
    main()
