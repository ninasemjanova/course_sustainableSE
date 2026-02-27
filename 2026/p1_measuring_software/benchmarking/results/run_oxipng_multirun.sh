#!/bin/bash
set -euo pipefail

# Edit this list to the versions you want (old → new)
TOOLCHAINS=("nightly-2026-02-24")
RUNS=${RUNS:-3}   # how many times per toolchain

# Ensure deps
which perf >/dev/null 2>&1 || { echo "perf missing"; exit 1; }
rustup --version >/dev/null 2>&1 || { echo "rustup missing"; exit 1; }

# Clone oxipng once (reuse between runs)
if [ ! -d oxipng ]; then
  git clone https://github.com/oxipng/oxipng.git
fi
cd oxipng
git fetch --tags
git checkout v3.0.1

bench_folder=benchmark_$(date +%Y-%m-%d_%H-%M)
mkdir "$bench_folder"
echo "Benchmark run started at $(date). RUNS=$RUNS versions=${TOOLCHAINS[*]}" | tee "${bench_folder}/run_info.txt"

for version in "${TOOLCHAINS[@]}"; do
  rustup toolchain install "$version" --force
  for i in $(seq 1 "$RUNS"); do
    label="results_${version}_run${i}"
    echo ">>> $version run ${i}/${RUNS}"
    cargo +"$version" bench --locked --bench reductions --no-run
    sudo perf stat -e power/energy-pkg/ -o "${bench_folder}/${label}" \
      $(which cargo) +"$version" bench --locked --bench reductions
  done
done
