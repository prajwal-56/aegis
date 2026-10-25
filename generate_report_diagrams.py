"""
generate_report_diagrams.py - Generates architectural and algorithmic diagram images for the Aegis project report.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_architecture_diagram(output_path="results/fig1_architecture.png"):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Title
    ax.text(5, 5.6, "Aegis System Architecture & Algorithmic Pipeline", fontsize=14, fontweight="bold", ha="center")

    # Layer 1: Ingestion
    box_ingest = patches.FancyBboxPatch((0.5, 3.2), 2.5, 1.8, boxstyle="round,pad=0.2", facecolor="#E1F5FE", edgecolor="#0288D1", linewidth=2)
    ax.add_patch(box_ingest)
    ax.text(1.75, 4.6, "1. Network Ingestion", fontsize=11, fontweight="bold", ha="center", color="#01579B")
    ax.text(1.75, 4.0, "• Live Nmap Scanner (-sn)\n• Gateway & Subnet Sniffer\n• Synthetic Presets (BA/ER)\n• Multi-Tier Mock LAN", fontsize=8.5, ha="center")

    # Arrow 1
    ax.annotate("", xy=(3.4, 4.1), xytext=(2.9, 4.1), arrowprops=dict(arrowstyle="->", lw=2, color="#555555"))

    # Layer 2: Graph Construction
    box_graph = patches.FancyBboxPatch((3.5, 3.2), 2.8, 1.8, boxstyle="round,pad=0.2", facecolor="#FFF9C4", edgecolor="#FBC02D", linewidth=2)
    ax.add_patch(box_graph)
    ax.text(4.9, 4.6, "2. Topology Construction", fontsize=11, fontweight="bold", ha="center", color="#F57F17")
    ax.text(4.9, 4.0, "• Undirected Graph G=(V,E)\n• Anti-Clique Normalization\n• Gateway Star & Hierarchy\n• NetworkX Topology Engine", fontsize=8.5, ha="center")

    # Arrow 2
    ax.annotate("", xy=(6.8, 4.1), xytext=(6.2, 4.1), arrowprops=dict(arrowstyle="->", lw=2, color="#555555"))

    # Layer 3: Algorithm Core
    box_algo = patches.FancyBboxPatch((6.9, 2.5), 2.6, 2.7, boxstyle="round,pad=0.2", facecolor="#E8F5E9", edgecolor="#388E3C", linewidth=2)
    ax.add_patch(box_algo)
    ax.text(8.2, 4.8, "3. Algorithm Core", fontsize=11, fontweight="bold", ha="center", color="#1B5E20")
    ax.text(8.2, 4.2, "[A] Exact Solver\n• Branch & Bound O(1.465^n)\n• Matching Lower Bound\n• Degree-1 Reductions", fontsize=8, ha="center")
    ax.text(8.2, 3.3, "[B] 2-Approximation\n• Maximal Matching O(|E|)\n• Guaranteed <= 2*OPT", fontsize=8, ha="center")
    ax.text(8.2, 2.6, "[C] Greedy Heuristic\n• Max-Degree Greedy O(log Δ)", fontsize=8, ha="center")

    # Layer 4: Output & Analytics
    box_out = patches.FancyBboxPatch((1.5, 0.4), 6.5, 1.5, boxstyle="round,pad=0.2", facecolor="#F3E5F5", edgecolor="#8E24AA", linewidth=2)
    ax.add_patch(box_out)
    ax.text(4.75, 1.55, "4. Output, Visualization & Benchmarking", fontsize=11, fontweight="bold", ha="center", color="#4A148C")
    ax.text(4.75, 0.95, "• Optimal Sensor Placement Mapping (Crimson Monitors vs Monitored Endpoints)\n• Empirical Complexity Verification (Log-Scale Runtime Scaling)\n• CLI Terminal Summary & Overhead Reduction Analytics", fontsize=8.5, ha="center")

    # Arrow down
    ax.annotate("", xy=(6.5, 1.8), xytext=(8.0, 2.6), arrowprops=dict(arrowstyle="->", lw=2, color="#555555"))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Generated architecture diagram at {output_path}")

def generate_bb_flowchart(output_path="results/fig2_flowchart.png"):
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5, 6.7, "Branch-and-Bound Exact Solver Logic Flow", fontsize=13, fontweight="bold", ha="center")

    # Nodes
    boxes = [
        (patches.FancyBboxPatch((3.0, 5.7), 4.0, 0.6, boxstyle="round,pad=0.1", facecolor="#E3F2FD", edgecolor="#1976D2", lw=1.5), "Start: search(cover, remaining_edges)", 5.0, 6.0),
        (patches.FancyBboxPatch((3.0, 4.6), 4.0, 0.6, boxstyle="round,pad=0.1", facecolor="#FFF3E0", edgecolor="#F57C00", lw=1.5), "All edges covered? -> Update best_cover", 5.0, 4.9),
        (patches.FancyBboxPatch((2.5, 3.5), 5.0, 0.6, boxstyle="round,pad=0.1", facecolor="#FFEBEE", edgecolor="#D32F2F", lw=1.5), "Lower Bound Pruning: len(cover) + |Matching| >= best?", 5.0, 3.8),
        (patches.FancyBboxPatch((2.5, 2.4), 5.0, 0.6, boxstyle="round,pad=0.1", facecolor="#E8F8F5", edgecolor="#1ABC9C", lw=1.5), "Degree-1 Reduction: Any deg=1? Take its neighbor", 5.0, 2.7),
        (patches.FancyBboxPatch((0.5, 0.8), 4.0, 0.9, boxstyle="round,pad=0.1", facecolor="#EDE7F6", edgecolor="#673AB7", lw=1.5), "Branch 1: Include v with max degree\ncover = cover ∪ {v}\nRecurse on remaining edges", 2.5, 1.25),
        (patches.FancyBboxPatch((5.5, 0.8), 4.0, 0.9, boxstyle="round,pad=0.1", facecolor="#FCE4EC", edgecolor="#C2185B", lw=1.5), "Branch 2: Exclude v\ncover = cover ∪ N(v) (all neighbors)\nRecurse on remaining edges", 7.5, 1.25),
    ]

    for patch, text, tx, ty in boxes:
        ax.add_patch(patch)
        ax.text(tx, ty, text, fontsize=9, fontweight="bold", ha="center", va="center")

    # Arrows
    arrows = [
        ((5.0, 5.7), (5.0, 5.2)),
        ((5.0, 4.6), (5.0, 4.1)),
        ((5.0, 3.5), (5.0, 3.0)),
        ((4.0, 2.4), (2.5, 1.7)),
        ((6.0, 2.4), (7.5, 1.7)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.8, color="#333333"))

    ax.text(2.8, 2.2, "No -> Branch v", fontsize=8, color="#555555")
    ax.text(7.7, 3.8, "Yes -> Prune subtree", fontsize=8, color="#D32F2F", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Generated flowchart at {output_path}")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_bb_flowchart()
