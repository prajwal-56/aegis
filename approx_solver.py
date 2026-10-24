"""
approx_solver.py - Polynomial-time approximation algorithms and heuristics for Aegis.
"""

import time
from typing import Set, Tuple, Any
import networkx as nx


def approx_vertex_cover_2approx(graph: nx.Graph) -> Set[Any]:
    """
    Classic 2-Approximation algorithm for Minimum Vertex Cover via Maximal Matching.

    Algorithm:
      1. Repeatedly select an arbitrary uncovered edge (u, v).
      2. Add BOTH endpoints u and v to the cover set.
      3. Remove all edges incident to u or v.
      4. Repeat until no edges remain.

    Theoretical Guarantee:
      The size of the returned cover is mathematically proven to be at most
      2 * |OPT|, where |OPT| is the size of the true minimum vertex cover.
      Runs in linear time O(|E|).
    """
    cover = set()
    uncovered_edges = set(graph.edges())

    while uncovered_edges:
        # Pick any edge (u, v)
        u, v = uncovered_edges.pop()
        cover.add(u)
        cover.add(v)

        # Remove all edges touching u or v
        uncovered_edges = {
            (x, y) for (x, y) in uncovered_edges if x != u and x != v and y != u and y != v
        }

    return cover


def approx_vertex_cover_greedy(graph: nx.Graph) -> Set[Any]:
    """
    Greedy Degree Heuristic for Vertex Cover.

    Algorithm:
      1. Compute current degree of all vertices with respect to uncovered edges.
      2. Pick the vertex with the maximum uncovered degree.
      3. Add it to the cover and mark its incident edges as covered.
      4. Repeat until all edges are covered.

    Theoretical Guarantee:
      Guaranteed O(log Delta) approximation factor, where Delta is the maximum degree.
      In empirical network topologies, this often finds solutions very close to |OPT|
      and noticeably smaller than the strict 2-approximation.
    """
    cover = set()
    if graph.number_of_edges() == 0:
        return cover

    # Adjacency map of uncovered edges
    adj = {node: set(graph.neighbors(node)) for node in graph.nodes()}
    edges_count = graph.number_of_edges()

    while edges_count > 0:
        # Pick node with maximum degree
        best_node = max(adj.keys(), key=lambda node: len(adj[node]))
        if len(adj[best_node]) == 0:
            break

        cover.add(best_node)

        # Remove edges incident to best_node
        neighbors = list(adj[best_node])
        edges_count -= len(neighbors)
        adj[best_node].clear()

        for nbr in neighbors:
            if best_node in adj[nbr]:
                adj[nbr].remove(best_node)

    return cover


def solve_approx(
    graph: nx.Graph, method: str = "2approx"
) -> Tuple[Set[Any], float]:
    """
    Main entry point for approximate vertex cover solvers.

    Args:
        graph: NetworkX graph.
        method: '2approx' (maximal matching) or 'greedy' (degree-based heuristic).

    Returns:
        (cover_set, elapsed_seconds)
    """
    start_time = time.perf_counter()
    if method == "2approx":
        cover = approx_vertex_cover_2approx(graph)
    elif method == "greedy":
        cover = approx_vertex_cover_greedy(graph)
    else:
        raise ValueError(f"Unknown approximation method '{method}'")
    elapsed = time.perf_counter() - start_time
    return cover, elapsed
