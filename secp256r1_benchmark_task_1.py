"""
    Key Pair Generation Batch

    Task:
        -   Generate N pairs of static and ephemeral ECC key pairs.
        -   Measure the total time taken for key generation and calculate the average latency per key pair.
"""

import time
import matplotlib.pyplot as plt
 
from cryptography.hazmat.primitives.asymmetric import ec
from statistics import median, stdev

NS = (100, 1000, 10000)
RUNS = 50

def plot_results(all_data, summary):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
 
    panels = (
        (ax1, 1, "Avg per key pair (ms)", "Per-pair latency", False),
        (ax2, 0, "Total time (s)", "Total time (log-log)", True),
    )
 
    for ax, idx, ylabel, title, loglog in panels:
        # Individual runs
        for n, runs in zip(NS, all_data):
            ys = [run[idx] for run in runs]
            ax.scatter([n] * len(ys), ys, alpha=0.35, s=18)
 
        # Median line with +/- 1 SD error bars
        medians, sds = summary[idx]
        ax.errorbar(NS, medians, yerr=sds, marker="o", color="black",
                    capsize=5, linewidth=1.5, label="Median \u00b1 1 SD")
 
        ax.set_xscale("log")
        if loglog:
            ax.set_yscale("log")
        ax.set_xlabel("Batch size N")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
 
    plt.tight_layout()
    plt.savefig("keygen_benchmark.png", dpi=200)
    plt.show()

def KPGB_benchmark(n, verbose=True):
    curve = ec.SECP256R1()
 
    start = time.perf_counter()
    for _ in range(n):
        static_priv = ec.generate_private_key(curve)
        ephemeral_priv = ec.generate_private_key(curve)
    elapsed = time.perf_counter() - start
 
    total_time = elapsed
    avg_per_pair = elapsed / n * 1000
    avg_per_key = elapsed / (2 * n) * 1000
 
    if verbose:
        print(f"N = {n:>5} | Total: {total_time:.4f}s | "
              f"Avg per pair: {avg_per_pair:.4f}ms | "
              f"Avg per key: {avg_per_key:.4f}ms")
 
    return total_time, avg_per_pair, avg_per_key

def summarize(all_data):
    """Return {metric_index: (medians, sds)} with one entry per batch size."""
    summary = {}
    for idx in range(3):  # 0 = total, 1 = per pair, 2 = per key
        medians, sds = [], []
        for runs in all_data:
            values = [run[idx] for run in runs]
            medians.append(median(values))
            sds.append(stdev(values))
        summary[idx] = (medians, sds)
    return summary

def print_summary(summary):
    print(f"{'N':>6} | {'Median total (s)':>17} | {'SD total (s)':>13} | "
          f"{'Median pair (ms)':>17} | {'SD pair (ms)':>13} | "
          f"{'Median key (ms)':>16} | {'SD key (ms)':>12}")
    print("-" * 112)
    for i, n in enumerate(NS):
        print(f"{n:>6} | {summary[0][0][i]:>17.4f} | {summary[0][1][i]:>13.5f} | "
              f"{summary[1][0][i]:>17.5f} | {summary[1][1][i]:>13.5f} | "
              f"{summary[2][0][i]:>16.5f} | {summary[2][1][i]:>12.5f}")

def main():

    # Warmup pass (not recorded)
    print()
    for n in NS:
        KPGB_benchmark(n)
    print()
 
    # Recorded runs: all_data[i] holds RUNS tuples for batch size NS[i]
    all_data = [[KPGB_benchmark(n, verbose=False) for _ in range(RUNS)] for n in NS]
 
    summary = summarize(all_data)
    print_summary(summary)
    plot_results(all_data, summary)

if __name__ == "__main__":
    main()