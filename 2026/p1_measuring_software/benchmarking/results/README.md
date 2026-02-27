# Benchmark results

Place benchmark result files here when sharing (e.g. copy from `oxipng/benchmark_YYYY-MM-DD_HH-MM/` after running `run_oxipng_benchmarks.sh`).

Example filenames produced by the script: `results_nightly-2024-06-15`, `results_nightly-2023-01-10`, etc.

Running the script multiple times and adding a run identifier (e.g. `run1_results_nightly-...`) helps with checking significance across runs.

## Commands we used (server → laptop)

Server (once per fresh machine):
```
sudo apt update
sudo apt install -y linux-tools-5.15.0-170-generic linux-cloud-tools-5.15.0-170-generic linux-tools-generic
sudo ln -sf /usr/lib/linux-tools-5.15.0-170-generic/perf /usr/bin/perf
sudo sh -c 'echo -1 > /proc/sys/kernel/perf_event_paranoid'
```

Server (benchmarks):
```
cd ~/course_sustainableSE/2026/p1_measuring_software/benchmarking
chmod +x run_oxipng_benchmarks.sh
# warm-up once per toolchain (not recorded)
./run_oxipng_multirun.sh >/tmp/warmup.log 2>&1
# measured runs (example: 20 repeats per toolchain)
RUNS=20 ./run_oxipng_multirun.sh | tee last_run.log
LATEST=$(ls -td oxipng/benchmark_* | head -1)
tar czvf benchmark_results.tar.gz "$LATEST"
```

Laptop (pull and place results):
```
cd ~/sustainable/course_sustainableSE
scp root@138.201.32.162:~/course_sustainableSE/2026/p1_measuring_software/benchmarking/benchmark_results.tar.gz .
tar xzvf benchmark_results.tar.gz
mv oxipng/benchmark_*/results_* 2026/p1_measuring_software/benchmarking/results/
mv oxipng/benchmark_*/run_info.txt 2026/p1_measuring_software/benchmarking/results/ 2>/dev/null || true
```

Aggregation (in `results/`):
```
python3 - <<'PY'
import glob, re, statistics, pathlib

def parse(path):
    joule = secs = None
    with open(path) as f:
        for line in f:
            if 'Joules' in line:
                try: joule = float(line.split()[0].replace(',', ''))
                except: pass
            if 'seconds time elapsed' in line:
                try: secs = float(line.split()[0].replace(',', ''))
                except: pass
    return joule, secs

pattern = re.compile(r"results_(nightly-\d{4}-\d{2}-\d{2})(?:_run(\d+))?")
rows = []
for path in glob.glob("results_*"):
    m = pattern.match(path)
    if not m: continue
    version = m.group(1)
    run = int(m.group(2) or 1)
    j, s = parse(path)
    if j is not None and s is not None:
        rows.append((version, run, j, s))

if not rows:
    print("No parsable results_* files found"); exit()

by = {}
for v, run, j, s in rows:
    by.setdefault(v, {"j": [], "s": []})
    by[v]["j"].append(j); by[v]["s"].append(s)

out = pathlib.Path("AVERAGES.md")
with out.open("w") as f:
    f.write("# Oxipng energy averages\n\n")
    f.write("| Rust toolchain | mean energy (J) | stdev | mean time (s) | stdev |\n")
    f.write("|---|---|---|---|---|\n")
    for v in sorted(by):
        J, S = by[v]["j"], by[v]["s"]
        f.write(f\"| {v} | {statistics.mean(J):.2f} | {statistics.pstdev(J) if len(J)>1 else 0:.2f} | "
                f\"{statistics.mean(S):.2f} | {statistics.pstdev(S) if len(S)>1 else 0:.2f} |\\n\")
print(f\"Wrote {out}\")
PY
```

Environment log: see `server_info.txt` for CPU/OS/perf details used during the runs.
