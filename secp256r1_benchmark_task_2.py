"""
    Shared Secret Derivation Batch

    Task:
        -   Using pre-generated or dynamically generated key pairs, derive N shared secret keys using ECDH
            point multiplication.
        -   Measure the total time taken to generate the batch of N shared secrets and calculate the average
            derivation time per shared secret.
"""

import time
import matplotlib.pyplot as plt
 
from cryptography.hazmat.primitives.asymmetric import ec
from statistics import median, stdev

NS = (100, 1000, 10000)
RUNS = 50

def SSDB_benchmark(n, verbose=True):
    """Derive n ECDH shared secrets. Returns (total_s, avg_per_secret_ms)."""
    curve = ec.SECP256R1()
 
    # Setup (NOT timed): pre-generate N key pairs for Alice and Bob
    alice_keys = [ec.generate_private_key(curve) for _ in range(n)]
    bob_pubs = [ec.generate_private_key(curve).public_key() for _ in range(n)]
 
    # Timed section: only the ECDH point multiplication
    start = time.perf_counter()
    for i in range(n):
        shared_key = alice_keys[i].exchange(ec.ECDH(), bob_pubs[i])
    elapsed = time.perf_counter() - start
 
    total_time = elapsed
    avg_per_shared_secret = elapsed / n * 1000
 
    if verbose:
        print(f"N = {n:>5} | Total: {total_time:.4f}s | "
              f"Avg per shared secret: {avg_per_shared_secret:.4f}ms")
 
    return total_time, avg_per_shared_secret
 
 
def summarize(all_data):
    """Return {metric_index: (medians, sds)} with one entry per batch size."""
    summary = {}
    for idx in range(2):  # 0 = total, 1 = per shared secret
        medians, sds = [], []
        for runs in all_data:
            values = [run[idx] for run in runs]
            medians.append(median(values))
            sds.append(stdev(values))
        summary[idx] = (medians, sds)
    return summary
 
 
def print_summary(summary):
    print(f"{'N':>6} | {'Median total (s)':>17} | {'SD total (s)':>13} | "
          f"{'Median secret (ms)':>19} | {'SD secret (ms)':>15}")
    print("-" * 82)
    for i, n in enumerate(NS):
        print(f"{n:>6} | {summary[0][0][i]:>17.4f} | {summary[0][1][i]:>13.5f} | "
              f"{summary[1][0][i]:>19.5f} | {summary[1][1][i]:>15.5f}")
 
 
def plot_results(all_data, summary):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
 
    panels = (
        (ax1, 1, "Avg per shared secret (ms)", "Per-secret latency", False),
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
    plt.savefig("shared_secret_benchmark.png", dpi=200)
    plt.show()
 
 
def main():
    # Warmup pass (not recorded)
    print()
    for n in NS:
        SSDB_benchmark(n)
    print()
 
    # Recorded runs: all_data[i] holds RUNS tuples for batch size NS[i]
    all_data = [[SSDB_benchmark(n, verbose=False) for _ in range(RUNS)] for n in NS]
 
    summary = summarize(all_data)
    print_summary(summary)
    plot_results(all_data, summary)
 
 
if __name__ == "__main__":
    main()