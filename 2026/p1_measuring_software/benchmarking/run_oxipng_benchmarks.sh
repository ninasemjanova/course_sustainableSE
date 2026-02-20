#!/bin/bash
# P1 2026 — Oxipng energy benchmarks across Rust toolchains.
# Run from this directory (or any dir where cloning oxipng is OK).
# Creates oxipng/ and a timestamped benchmark_* folder with perf results.
#
# Usage:
#   ./run_oxipng_benchmarks.sh         # full run (6 toolchains, ~30–60 min)
#   ./run_oxipng_benchmarks.sh quick   # quick run (2 toolchains, ~10–15 min)

COUNT=5
[[ "${1:-}" == "quick" ]] && COUNT=1

git clone https://github.com/oxipng/oxipng.git
cd oxipng
git checkout 'v3.0.1'

# Test if rustc is installed if not, install it.
rustup --version  &>/dev/null
if [[ $? -ne 0 ]]
then
    echo No functioning Rustup, installing Rustup.
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    exit # Exit early because env variables need reloading
fi

# Test if CC is installed if not, install it
which cc &>/dev/null || (sudo apt update; sudo apt install build-essential -y)
which perf &>/dev/null || (sudo apt update; sudo apt install linux-tools-common linux-tools-generic "linux-tools-$(uname -r)" -y)

# Create a folder with the test results
bench_folder=benchmark_`date +%Y-%m-%d_%H-%M`
if [[ -d "./$bench_folder" ]]
then
    echo Benchmark folder already exists. Exiting
    exit 1
fi
mkdir ./"$bench_folder"
echo "Benchmark run started at $(date). COUNT=$COUNT (toolchains: $((COUNT+1)))." | tee "${bench_folder}/run_info.txt"

start_date=`date +%s`
end_date=`date -d "2020-01-30" +%s` # The day the minimum supported Rust version of is 1.41.0 was released

diff=$(( start_date - end_date ))
steps=$(( diff / COUNT ))

for ((i=0; i<=COUNT; i++))
do
    current_ts=$(( start_date - (i * steps) ))
    version=nightly-`date -d "@$current_ts" +"%Y-%m-%d"`
    echo Running testing on $version 

    rustup toolchain install "$version" --force
    
    # Compile oxipng with the correct rust version
    cargo +"$version" bench --locked --bench reductions --no-run

    # Run the benchmarks and log
    sudo perf stat -e power/energy-pkg/ -o "${bench_folder}/results_${version}" `which cargo` +"$version" bench --locked --bench reductions
done
