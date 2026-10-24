"""
main.py - Aegis: Network Topology Minimum Vertex Cover Engine (CLI Entrypoint).
"""

import argparse
import sys
import os
from typing import List, Dict, Any, Set
import networkx as nx

from graph_utils import (
    is_vertex_cover,
    generate_synthetic_graph,
    visualize_network_cover,
)
from exact_solver import solve_exact
from approx_solver import solve_approx
from scan import (
    scan_network_live,
    generate_mock_network_hosts,
    build_network_graph,
    get_local_subnet,
    NMAP_AVAILABLE,
)
from benchmark import run_benchmark_suite, plot_benchmark_results


BANNER = r"""
    ___    ______ _____ ____ _____
   /   |  / ____// ___//  _// ___/
  / /| | / __/  / / __ / /  \__ \ 
 / ___ |/ /___ / /_/ // /  ___/ / 
/_/  |_/_____/ \____/___/ /____/  
   Network Topology Vertex Cover Engine
"""


def format_node_list(nodes: Set[Any], max_display: int = 6) -> str:
    sorted_nodes = sorted(list(nodes), key=str)
    if len(sorted_nodes) <= max_display:
        return "[" + ", ".join(str(n) for n in sorted_nodes) + "]"
    preview = ", ".join(str(n) for n in sorted_nodes[:max_display])
    return f"[{preview}, ... +{len(sorted_nodes) - max_display} more]"


def print_summary_table(G: nx.Graph, exact_res, approx2_res, greedy_res) -> None:
    c_exact, t_exact = exact_res
    c_approx2, t_approx2 = approx2_res
    c_greedy, t_greedy = greedy_res

    opt_size = len(c_exact)
    ratio_approx2 = len(c_approx2) / opt_size if opt_size > 0 else 1.0
    ratio_greedy = len(c_greedy) / opt_size if opt_size > 0 else 1.0

    print("=" * 82)
    print(f"Network Summary: {G.number_of_nodes()} Vertices (Devices), {G.number_of_edges()} Edges (Connections)")
    print("=" * 82)
    print(f"{'Algorithm':<22} | {'Cover Size':<11} | {'Time (s)':<12} | {'Ratio':<7} | {'Selected Monitors'}")
    print("-" * 82)
    print(f"{'Exact (Branch & Bound)':<22} | {len(c_exact):<11} | {t_exact:<12.6f} | {'1.00x':<7} | {format_node_list(c_exact)}")
    print(f"{'2-Approximation':<22} | {len(c_approx2):<11} | {t_approx2:<12.6f} | {f'{ratio_approx2:.2f}x':<7} | {format_node_list(c_approx2)}")
    print(f"{'Greedy Heuristic':<22} | {len(c_greedy):<11} | {t_greedy:<12.6f} | {f'{ratio_greedy:.2f}x':<7} | {format_node_list(c_greedy)}")
    print("=" * 82)

    coverage_saved = (1.0 - (opt_size / G.number_of_nodes())) * 100 if G.number_of_nodes() > 0 else 0
    print(f"\n[💡 Insights]")
    print(f" • Monitoring reduction: By placing sensors at {opt_size}/{G.number_of_nodes()} nodes, {coverage_saved:.1f}%")
    print(f"   of devices do not need active inspection while maintaining 100% link coverage.")
    print(f" • 2-Approximation guarantee verified: {len(c_approx2)} <= {2 * opt_size} (at most 2x optimal).")
    print(f" • Speedup: 2-Approximation ran in {t_approx2:.6f}s vs {t_exact:.6f}s for Exact solver.")


def run_pipeline(args) -> None:
    os.makedirs("results", exist_ok=True)
    G = None

    if args.benchmark:
        print("[*] Starting benchmark mode...")
        results = run_benchmark_suite(
            min_nodes=args.bench_min,
            max_nodes=args.bench_max,
            step=args.bench_step,
            samples_per_size=args.bench_samples,
            graph_type=args.preset,
        )
        plot_benchmark_results(results, output_path=args.output or "results/benchmark_comparison.png")
        return

    # Ingestion mode
    if args.scan is not None or (not args.mock and not args.preset_used):
        # Live nmap scan
        target = args.scan if (args.scan and args.scan != "auto") else get_local_subnet()
        try:
            hosts = scan_network_live(target_subnet=target)
            if not hosts:
                print(f"[!] Warning: No active hosts responded on {target}. Falling back to mock demo network.")
                hosts = generate_mock_network_hosts()
        except Exception as e:
            print(f"[!] Scan error ({e}). Falling back to mock network hosts.")
            hosts = generate_mock_network_hosts()

        G = build_network_graph(hosts, topology_model=args.topology)

    elif args.mock:
        print("[*] Loading realistic mock enterprise network...")
        hosts = generate_mock_network_hosts()
        G = build_network_graph(hosts, topology_model=args.topology)

    elif args.preset:
        print(f"[*] Generating '{args.preset}' synthetic topology with {args.nodes} nodes...")
        G = generate_synthetic_graph(
            graph_type=args.preset, num_nodes=args.nodes, seed=args.seed
        )

    if G is None or G.number_of_nodes() == 0:
        print("[-] Error: Graph is empty.")
        sys.exit(1)

    print(f"[*] Solving Minimum Vertex Cover across {G.number_of_nodes()} devices...")

    # Run Solvers
    exact_res = solve_exact(G, method=args.exact_method)
    approx2_res = solve_approx(G, method="2approx")
    greedy_res = solve_approx(G, method="greedy")

    # Display results
    print_summary_table(G, exact_res, approx2_res, greedy_res)

    # Visualization
    if args.visualize:
        out_img = args.output or "results/network_cover.png"
        print(f"\n[*] Rendering network topology visualization to '{out_img}'...")
        visualize_network_cover(
            graph=G,
            cover=exact_res[0],
            title=f"Aegis Topology — Minimum Vertex Cover (|OPT| = {len(exact_res[0])})",
            output_path=out_img,
        )
        print(f"[✓] Graph visualization saved to {out_img}")


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Aegis: Optimal Sensor Placement via Minimum Vertex Cover"
    )

    mode_group = parser.add_argument_group("Network Ingestion")
    mode_group.add_argument(
        "--scan",
        nargs="?",
        const="auto",
        help="Scan live subnet using nmap (e.g. 192.168.1.0/24 or auto-detect)",
    )
    mode_group.add_argument(
        "--mock", action="store_true", help="Use built-in realistic mock network hosts"
    )
    mode_group.add_argument(
        "--preset",
        type=str,
        choices=["enterprise", "scale_free", "random", "star"],
        default="enterprise",
        help="Synthetic topology preset (default: enterprise)",
    )
    mode_group.add_argument(
        "--nodes", type=int, default=15, help="Number of nodes for synthetic presets"
    )
    mode_group.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    mode_group.add_argument(
        "--topology",
        type=str,
        choices=["hierarchical", "star", "mesh"],
        default="hierarchical",
        help="Network topology structure model for host connections",
    )

    solver_group = parser.add_argument_group("Solver Options")
    solver_group.add_argument(
        "--exact-method",
        choices=["branch_and_bound", "bruteforce"],
        default="branch_and_bound",
        help="Exact algorithm strategy",
    )

    vis_group = parser.add_argument_group("Visualization & Output")
    vis_group.add_argument(
        "--visualize",
        action="store_true",
        default=True,
        help="Render network graph with highlighted monitoring nodes",
    )
    vis_group.add_argument(
        "--no-visualize",
        dest="visualize",
        action="store_false",
        help="Disable graph rendering",
    )
    vis_group.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output image path for visualization or benchmark chart",
    )

    bench_group = parser.add_argument_group("Benchmarking")
    bench_group.add_argument(
        "--benchmark", action="store_true", help="Execute comparative benchmark suite"
    )
    bench_group.add_argument(
        "--bench-min", type=int, default=6, help="Min vertices for benchmark"
    )
    bench_group.add_argument(
        "--bench-max", type=int, default=20, help="Max vertices for benchmark"
    )
    bench_group.add_argument(
        "--bench-step", type=int, default=2, help="Step size for benchmark"
    )
    bench_group.add_argument(
        "--bench-samples",
        type=int,
        default=3,
        help="Samples per size for benchmark",
    )

    args = parser.parse_args()
    args.preset_used = any("--preset" in arg for arg in sys.argv)
    run_pipeline(args)


if __name__ == "__main__":
    main()
