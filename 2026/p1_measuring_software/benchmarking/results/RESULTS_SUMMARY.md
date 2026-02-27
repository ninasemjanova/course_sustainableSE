# Benchmark results summary

**Dataset:** 15 Rust nightlies, **20 measured runs per toolchain** (`results_nightly-*_run1..run20`)  
**Target:** oxipng v3.0.1, `reductions` benchmark  
**Measurement:** `perf stat -e power/energy-pkg/` (CPU package energy, Joules)  
**Environment:** Ubuntu 22.04.5, Intel i7-6700, Linux 5.15 (see `server_info.txt`)

---

## Main findings

1. **Best overall point in this dataset is `nightly-2025-06-01`.**  
   Mean energy: **1460.62 J**, mean time: **61.73 s**.

2. **Compared to baseline `nightly-2020-01-30`, `nightly-2025-06-01` is much better:**  
   Energy: **-38.17%** (2362.17 J -> 1460.62 J)  
   Time: **-43.37%** (109.00 s -> 61.73 s)

3. **Recent versions remain better than 2020 baseline, but regress vs the 2025-06 best.**  
   `nightly-2026-02-24` vs baseline: energy **-29.06%**, time **-31.72%**.  
   `nightly-2026-02-24` vs 2025-06: energy **+14.72%**, time **+20.57%**.

4. **Trend is not monotonic.**  
   Performance/energy improves strongly overall from 2020 to mid-2025, then worsens in late-2025/early-2026 while still staying above 2020 levels.

---

## Mean results by toolchain

| Rust toolchain | runs | mean energy (J) | stdev | mean time (s) | stdev |
|---|---|---|---|---|---|
| nightly-2020-01-30 | 20 | 2362.17 | 52.34 | 109.00 | 2.53 |
| nightly-2020-06-01 | 20 | 2405.46 | 99.73 | 111.66 | 3.61 |
| nightly-2021-03-01 | 20 | 2157.05 | 119.19 | 94.52 | 3.96 |
| nightly-2021-06-01 | 20 | 2028.44 | 104.96 | 89.68 | 5.77 |
| nightly-2021-08-01 | 20 | 2037.15 | 88.61 | 89.09 | 4.94 |
| nightly-2022-09-01 | 20 | 1814.68 | 84.54 | 77.86 | 2.79 |
| nightly-2023-01-01 | 20 | 1774.13 | 96.51 | 75.80 | 3.56 |
| nightly-2023-06-01 | 20 | 1644.74 | 58.75 | 67.96 | 2.00 |
| nightly-2024-06-01 | 20 | 1602.48 | 70.40 | 70.35 | 3.51 |
| nightly-2024-12-01 | 20 | 1580.13 | 83.69 | 69.25 | 3.06 |
| nightly-2025-06-01 | 20 | 1460.62 | 65.37 | 61.73 | 3.12 |
| nightly-2025-09-01 | 20 | 1584.20 | 71.53 | 67.52 | 3.37 |
| nightly-2025-12-01 | 20 | 1569.46 | 57.93 | 67.54 | 2.84 |
| nightly-2026-01-01 | 20 | 1664.90 | 53.67 | 74.73 | 2.57 |
| nightly-2026-02-24 | 20 | 1675.67 | 55.65 | 74.43 | 2.58 |

---

## Visualization files

- `benchmarking/results/plots/energy_violin_box.png`
- `benchmarking/results/plots/time_violin_box.png`
- `benchmarking/results/plots/energy_vs_time_versions.png`
- `benchmarking/results/stats/energy_time_regression.png`
- `benchmarking/results/stats/stats_summary.md`
- `benchmarking/results/stats/anova_tukey_energy.csv`
- `benchmarking/results/stats/anova_tukey_time.csv`

---

## Statistical tests

Using all `300` runs (`15` toolchains x `20` runs):

- One-way ANOVA on energy across toolchains: `F(14, 285) = 282.60`, `p = 6.99e-158`, eta^2 `= 0.933`.
- One-way ANOVA on time across toolchains: `F(14, 285) = 390.91`, `p = 9.49e-177`, eta^2 `= 0.951`.
- Linear model (energy vs time, all runs):  
  `energy_J = 268.69 + 19.42 * time_s`  
  `R^2 = 0.964`, `r = 0.982`, `p = 5.42e-218` (slope 95% CI: `[19.00, 19.85]` J/s).
- Linear model on per-version means (`n=15`) gives similar relation:  
  `R^2 = 0.986`, `p = 2.43e-13`.

Interpretation: toolchain version has a statistically significant effect on both energy and runtime, and energy is very strongly linearly associated with runtime in this benchmark.

---

## Caveats

- `power/energy-pkg/` measures CPU package energy only, not whole-system energy.
- Results are machine-specific (CPU, governor, kernel, background load).
- Even with 20 runs, benchmark noise exists; distributions (violin/box plots) should be checked together with means.
