"""
benchmark.py - Benchmarks exact vs approximate solvers across graph sizes and topologies.
"""

import argparse
import time
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import networkx as nx
from graph_utils import generate_synthetic_graph
from exact_solver import solve_exact
from approx_solver import solve_approx


def run_benchmark_suite(
    min_nodes: int = 4,
    max_nodes: int = 24,
    step: int = 2,
    samples_per_size: int = 3,
    graph_type: str = "scale_free",
) -> Dict[str, List[float]]:
    """
    Evaluates runtime and cover sizes for Exact (B&B), 2-Approximation,
    and Greedy heuristic across increasing graph sizes.
    """
    sizes = list(range(min_nodes, max_nodes + 1, step))
    results: Dict[str, List[float]] = {
        "sizes": sizes,
        "exact_time": [],
        "approx_2_time": [],
        "greedy_time": [],
        "exact_size": [],
        "approx_2_size": [],
        "greedy_size": [],
        "approx_2_ratio": [],
        "greedy_ratio": [],
    }

    print(f"\n[+] Running benchmark on '{graph_type}' topologies ({min_nodes} -> {max_nodes} nodes)...")
    print("-" * 75)
    print(f"{'Nodes':<8} | {'Exact (s)':<12} | {'2-Approx (s)':<12} | {'Greedy (s)':<12} | {'Approx Ratio':<12}")
    print("-" * 75)

    for n in sizes:
        exact_times = []
        approx_times = []
        greedy_times = []

        exact_sizes = []
        approx_sizes = []
        greedy_sizes = []

        for sample in range(samples_per_size):
            seed = 1000 * n + sample
            G = generate_synthetic_graph(graph_type=graph_type, num_nodes=n, seed=seed)

            # 1. Exact Solver
            c_exact, t_exact = solve_exact(G, method="branch_and_bound")
            exact_times.append(t_exact)
            exact_sizes.append(len(c_exact))

            # 2. 2-Approximation
            c_approx, t_approx = solve_approx(G, method="2approx")
            approx_times.append(t_approx)
            approx_sizes.append(len(c_approx))

            # 3. Greedy Heuristic
            c_greedy, t_greedy = solve_approx(G, method="greedy")
            greedy_times.append(t_greedy)
            greedy_sizes.append(len(c_greedy))

        avg_t_exact = sum(exact_times) / len(exact_times)
        avg_t_approx = sum(approx_times) / len(approx_times)
        avg_t_greedy = sum(greedy_times) / len(greedy_times)

        avg_sz_exact = sum(exact_sizes) / len(exact_sizes)
        avg_sz_approx = sum(approx_sizes) / len(approx_sizes)
        avg_sz_greedy = sum(greedy_sizes) / len(greedy_sizes)

        ratio_2 = avg_sz_approx / avg_sz_exact if avg_sz_exact > 0 else 1.0
        ratio_greedy = avg_sz_greedy / avg_sz_exact if avg_sz_exact > 0 else 1.0

        results["exact_time"].append(avg_t_exact)
        results["approx_2_time"].append(avg_t_approx)
        results["greedy_time"].append(avg_t_greedy)

        results["exact_size"].append(avg_sz_exact)
        results["approx_2_size"].append(avg_sz_approx)
        results["greedy_size"].append(avg_sz_greedy)

        results["approx_2_ratio"].append(ratio_2)
        results["greedy_ratio"].append(ratio_greedy)

        print(
            f"{n:<8} | {avg_t_exact:<12.6f} | {avg_t_approx:<12.6f} | {avg_t_greedy:<12.6f} | {ratio_2:<12.2f}"
        )

    print("-" * 75)
    return results


def plot_benchmark_results(results: Dict[str, List[float]], output_path: str = "results/benchmark_comparison.png") -> None:
    """
    Generates side-by-side plots:
      1. Runtime scaling (log-scale) comparing exponential vs polynomial algorithms.
      2. Cover size / Solution quality comparison.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    sizes = results["sizes"]

    # 1. Runtime Comparison
    ax1.plot(sizes, results["exact_time"], "ro-", linewidth=2, label="Exact (Branch & Bound)")
    ax1.plot(sizes, results["approx_2_time"], "bs-", linewidth=2, label="2-Approximation (Maximal Matching)")
    ax1.plot(sizes, results["greedy_time"], "g^-", linewidth=2, label="Greedy Degree Heuristic")
    ax1.set_title("Runtime Scaling Comparison", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Network Size (Vertices)", fontsize=11)
    ax1.set_ylabel("Execution Time (Seconds) [Log Scale]", fontsize=11)
    ax1.set_yscale("log")
    ax1.grid(True, which="both", linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left")

    # 2. Cover Size Comparison
    ax2.plot(sizes, results["exact_size"], "ro-", linewidth=2, label="Exact Optimal |OPT|")
    ax2.plot(sizes, results["approx_2_size"], "bs-", linewidth=2, label="2-Approximation Cover")
    ax2.plot(sizes, results["greedy_size"], "g^-", linewidth=2, label="Greedy Cover")
    # Plot 2*OPT theoretical ceiling
    two_opt_ceiling = [2 * s for s in results["exact_size"]]
    ax2.plot(sizes, two_opt_ceiling, "k--", alpha=0.5, label="Theoretical Bound (2 * |OPT|)")

    ax2.set_title("Vertex Cover Solution Quality", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Network Size (Vertices)", fontsize=11)
    ax2.set_ylabel("Cover Size (# of Monitored Nodes)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"\n[✓] Benchmark chart successfully saved to: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Aegis Vertex Cover Benchmark Suite")
    parser.add_argument("--min-nodes", type=int, default=6, help="Minimum number of vertices")
    parser.add_argument("--max-nodes", type=int, default=24, help="Maximum number of vertices")
    parser.add_argument("--step", type=int, default=2, help="Step size between vertex counts")
    parser.add_argument("--samples", type=int, default=3, help="Samples per graph size")
    parser.add_argument("--topology", type=str, default="scale_free", choices=["scale_free", "random", "enterprise"], help="Topology type")
    parser.add_argument("--output", type=str, default="results/benchmark_comparison.png", help="Path to save output chart")
    args = parser.parse_args()

    results = run_benchmark_suite(
        min_nodes=args.min_nodes,
        max_nodes=args.max_nodes,
        step=args.step,
        samples_per_size=args.samples,
        graph_type=args.topology,
    )
    plot_benchmark_results(results, output_path=args.output)


if __name__ == "__main__":
    main()
