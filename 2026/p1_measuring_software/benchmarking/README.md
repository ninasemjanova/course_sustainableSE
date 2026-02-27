# P1 Benchmarking — Oxipng energy across Rust toolchains

This folder contains the benchmarking work for the 2026 P1 "Measuring Software" project: measuring **energy consumption** of [oxipng](https://github.com/oxipng/oxipng) (PNG optimizer in Rust) across different Rust compiler versions.

## What’s in here

| File / folder | Description |
|---------------|-------------|
| `run_oxipng_benchmarks.sh` | Script that runs energy benchmarks with `perf` (power/energy-pkg) for several Rust nightlies. |
| `plot_benchmarks.py` | Parses `results_nightly-*` files and creates Matplotlib violin+box visualizations for energy and runtime. |
| `run_stats.py` | Runs ANOVA and linear regression on `results_nightly-*_run*`, writes a stats summary, Tukey CSV outputs, and regression plot. |
| `results/` | Place to store or link benchmark result files (e.g. from server runs) so they’re in one place. |

## Work done so far

- **Script:** Written and used to run benchmarks (clones oxipng v3.0.1, installs Rust nightlies, builds and runs the `reductions` bench under `perf stat -e power/energy-pkg/`).
- **Benchmarks:** Some benchmark runs have already been collected.
- **Next steps:** Run the script several more times (e.g. on the same server) to get multiple samples per toolchain and check if differences are significant (e.g. mean ± std or confidence intervals).

## Produce results (run on the server)

The script needs Linux and `perf` (energy counters). **→ See [RUN_ON_SERVER.md](RUN_ON_SERVER.md)** for step-by-step: SSH, run `./run_oxipng_benchmarks.sh quick` (2 toolchains, ~10–15 min), then copy the result files back into `results/`.

Use **`./run_oxipng_benchmarks.sh quick`** first to get results quickly; use **`./run_oxipng_benchmarks.sh`** for the full 6-toolchain run.

---

## How to run the script (reference)

**Requirements:** Linux, `perf` (e.g. `linux-tools-$(uname -r)`), Rust (rustup), C compiler. Run from a directory where it’s OK to clone `oxipng` (e.g. a temp or project dir):

```bash
cd /path/to/benchmarking
chmod +x run_oxipng_benchmarks.sh
./run_oxipng_benchmarks.sh
```

The script will create a timestamped folder inside the cloned `oxipng` repo (e.g. `oxipng/benchmark_2026-02-20_14-30/`) with one result file per Rust version (e.g. `results_nightly-2024-06-15`). Copy those files into `results/` here if you want to version or share them.

## Sharing results

- **In this repo:** Put summary files or selected `results_*` outputs in `results/` and commit.
- **Elsewhere:** You can also keep full runs on a server or in a separate repo and link that from the P1 report.

## Create box/violin visualizations

Run from the repository root:

```bash
python3 benchmarking/plot_benchmarks.py
```

If Matplotlib is missing:

```bash
python3 -m pip install --user matplotlib
```

Outputs are written to `benchmarking/results/plots/`:

- `benchmark_samples.csv`
- `energy_violin_box.png`
- `time_violin_box.png`
- `energy_vs_time_versions.png`

## Run ANOVA and regression

```bash
python3 benchmarking/run_stats.py
```

Outputs are written to `benchmarking/results/stats/`:

- `stats_summary.md`
- `energy_time_regression.png`
- `anova_tukey_energy.csv`
- `anova_tukey_time.csv`

---

*Part of the 2026 Sustainable Software Engineering (P1) group work.*
