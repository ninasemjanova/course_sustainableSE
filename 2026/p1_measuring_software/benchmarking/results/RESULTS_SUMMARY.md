# Benchmark results summary

**Run:** 2026-02-20 (quick run, 2 Rust toolchains)  
**Target:** oxipng v3.0.1, `reductions` benchmark  
**Measurement:** `perf stat -e power/energy-pkg/` (package energy, Joules) on server Ubuntu 22.04.

---

## Energy and time per Rust toolchain

| Rust toolchain     | Energy (Joules) | Time (seconds) |
|--------------------|-----------------|----------------|
| nightly-2026-02-20 | **1,618.64**    | **76.96**      |
| nightly-2020-01-30 | 2,353.62        | 114.82         |

---

## What the results show

1. **Newer Rust uses less energy.** The 2026 nightly consumed **~31% less energy** than the 2020 nightly (1,619 J vs 2,354 J) for the same workload (oxipng reductions benchmark).

2. **Newer Rust is faster.** Wall-clock time dropped from ~115 s to ~77 s (**~33% faster**). So the energy gain is consistent with better performance (same work in less time → less energy).

3. **Interpretation.** Over ~6 years, compiler and runtime improvements (codegen, optimizations, stdlib) made this benchmark both faster and more energy-efficient. That fits the idea that “faster often means greener” when the workload is the same.

---

## Caveats

- **Single run per toolchain.** For stronger claims you’d run the script 2–3 times and report mean ± std (or confidence intervals) for energy and time.
- **Same machine.** Results are valid for this server (Ubuntu 22.04, same CPU); other hardware may differ.
- **energy-pkg.** This is package (CPU) energy only, not full system power.

---

*Data from files: `results_nightly-2026-02-20`, `results_nightly-2020-01-30`, `run_info.txt`.*

---

## Why these Rust versions

- `nightly-2020-01-30`: baseline near oxipng’s historical MSRV (Rust 1.41) to show an early starting point.
- `nightly-2021-03-01`, `nightly-2021-06-01`, `nightly-2021-08-01`: 2021 checkpoints capture mid-cycle optimizer/MIR and LLVM updates.
- `nightly-2022-09-01`: mid-2022 anchor to see gains after 2021.
- `nightly-2023-01-01`, `nightly-2023-06-01`: early and mid-2023 snapshots to track incremental codegen improvements.
- `nightly-2024-06-01`, `nightly-2024-12-01`: early/late 2024 to observe year-over-year deltas.
- `nightly-2025-06-01`, `nightly-2025-09-01`, `nightly-2025-12-01`: mid/late 2025 spread to catch newer LLVM and Rust backend work.
- `nightly-2026-01-01`, `nightly-2026-02-24`: near-tip compilers to compare the most recent optimizations against older baselines.
