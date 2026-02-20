# How to produce results on the server

The script needs **Linux** and **perf** (CPU energy counters), so run it on the lab server. Use the server details from your team chat.

---

## Copy-paste command sequence

Do these in order. Replace `YOUR_GITHUB_USERNAME` with your GitHub username if you use Option A.

### Step 0 — On your laptop (once): get the script to the server

**Option A — Push this repo to your GitHub fork, then on the server you’ll clone it (Step 2).**

**Option B — Upload the script without GitHub:**

```bash
cd /Users/mikolajmagiera/Desktop/code/Sustainable/course_sustainableSE
scp 2026/p1_measuring_software/benchmarking/run_oxipng_benchmarks.sh root@138.201.32.162:~/run_oxipng_benchmarks.sh
```
(Enter the server password when prompted.)

---

### Step 1 — On your laptop: SSH in

```bash
ssh root@138.201.32.162
```
(Enter password.)

---

### Step 2 — On the server: get script (if needed) and run

**If you used Option A (GitHub):**

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/course_sustainableSE.git
cd course_sustainableSE/2026/p1_measuring_software/benchmarking
chmod +x run_oxipng_benchmarks.sh
./run_oxipng_benchmarks.sh quick
```

**If you used Option B (scp):**

```bash
cd ~
mkdir -p p1_bench && cd p1_bench
mv ~/run_oxipng_benchmarks.sh .
chmod +x run_oxipng_benchmarks.sh
./run_oxipng_benchmarks.sh quick
```

Wait until it finishes (~10–15 min for quick run). You’ll see it install Rust, build oxipng, and run perf for 2 toolchains.

---

### Step 3 — On the server (after the run): pack the results

**If you used Option A:**

```bash
cd ~/course_sustainableSE/2026/p1_measuring_software/benchmarking
LATEST=$(ls -td oxipng/benchmark_* 2>/dev/null | head -1)
tar czvf benchmark_results.tar.gz "$LATEST"
```

**If you used Option B:**

```bash
cd ~/p1_bench
LATEST=$(ls -td oxipng/benchmark_* 2>/dev/null | head -1)
tar czvf benchmark_results.tar.gz "$LATEST"
```

---

### Step 4 — On your laptop (new terminal): download and unpack

Open a **new** terminal (don’t close the SSH session if you want to run again later).

**If you used Option A:**

```bash
cd /Users/mikolajmagiera/Desktop/code/Sustainable/course_sustainableSE
scp root@138.201.32.162:~/course_sustainableSE/2026/p1_measuring_software/benchmarking/benchmark_results.tar.gz .
tar xzvf benchmark_results.tar.gz
mv benchmark_*/results_* 2026/p1_measuring_software/benchmarking/results/
mv benchmark_*/run_info.txt 2026/p1_measuring_software/benchmarking/results/ 2>/dev/null || true
```

**If you used Option B:**

```bash
cd /Users/mikolajmagiera/Desktop/code/Sustainable/course_sustainableSE
scp root@138.201.32.162:~/p1_bench/benchmark_results.tar.gz .
tar xzvf benchmark_results.tar.gz
mv benchmark_*/results_* 2026/p1_measuring_software/benchmarking/results/
mv benchmark_*/run_info.txt 2026/p1_measuring_software/benchmarking/results/ 2>/dev/null || true
```

Done. Your result files are in `2026/p1_measuring_software/benchmarking/results/`. You can commit them.

---

## Detailed reference (same steps, more explanation)

### 1. SSH into the server

```bash
ssh root@138.201.32.162
# Enter the server password when prompted.
```

## 2. Get the script onto the server

**Option A — Clone the repo (if your work is pushed to GitHub):**

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/course_sustainableSE.git
cd course_sustainableSE/2026/p1_measuring_software/benchmarking
chmod +x run_oxipng_benchmarks.sh
```

**Option B — Copy-paste the script (if not pushed yet):**

```bash
cd ~
mkdir -p p1_bench && cd p1_bench
# Then create run_oxipng_benchmarks.sh (e.g. with nano) and paste the contents from
# 2026/p1_measuring_software/benchmarking/run_oxipng_benchmarks.sh
chmod +x run_oxipng_benchmarks.sh
```

## 3. Run the benchmarks

**Quick run first (2 toolchains, ~10–15 min) — recommended to get results fast:**

```bash
./run_oxipng_benchmarks.sh quick
```

**Full run later (6 toolchains, ~30–60 min):**

```bash
./run_oxipng_benchmarks.sh
```

The script will clone oxipng, install Rust toolchains, and write results into  
`oxipng/benchmark_YYYY-MM-DD_HH-MM/`.

## 4. Copy results back to your machine

On the **server**, create a tarball of the latest benchmark folder:

```bash
cd ~/course_sustainableSE/2026/p1_measuring_software/benchmarking   # or ~/p1_bench
LATEST=$(ls -td oxipng/benchmark_* 2>/dev/null | head -1)
tar czvf benchmark_results.tar.gz "$LATEST"
```

Then on **your laptop** (in a new terminal, from your project root):

```bash
scp root@138.201.32.162:~/course_sustainableSE/2026/p1_measuring_software/benchmarking/benchmark_results.tar.gz .
# Or if you used Option B: scp root@138.201.32.162:~/p1_bench/benchmark_results.tar.gz .
tar xzvf benchmark_results.tar.gz
# Move the result files into the repo:
mv benchmark_*/results_* 2026/p1_measuring_software/benchmarking/results/
mv benchmark_*/run_info.txt 2026/p1_measuring_software/benchmarking/results/
```

You can then commit the files in `2026/p1_measuring_software/benchmarking/results/`.

## 5. Run multiple times (for significance)

Run the script 2–3 times (e.g. `quick` or full), each time copy the new `benchmark_*` folder and add the result files to `results/` with a run id, e.g.:

- `results/run1_results_nightly-2024-06-15`
- `results/run2_results_nightly-2024-06-15`

Then you can compare mean energy across runs.

---

**Troubleshooting**

- **`perf` permission denied:** The script uses `sudo perf stat ...`. If you get permission errors, run the whole script with `sudo` or fix perf permissions (e.g. `echo -1 | sudo tee /proc/sys/kernel/perf_event_paranoid`).
- **Rust not found after install:** If rustup was just installed, run `source $HOME/.cargo/env` or log out and back in, then run the script again.
- **Out of disk:** The script uses several GB (Rust toolchains + oxipng). Free space with `df -h`; remove old toolchains with `rustup toolchain list` and `rustup toolchain uninstall <name>`.
