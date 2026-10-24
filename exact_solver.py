"""
exact_solver.py - Exact Minimum Vertex Cover algorithms for Aegis.
"""

import time
import itertools
from typing import Set, Tuple, Any, Optional
import networkx as nx
from graph_utils import is_vertex_cover


def exact_vertex_cover_bruteforce(graph: nx.Graph) -> Set[Any]:
    """
    Finds the exact minimum vertex cover by testing subset combinations
    of increasing size k = 0, 1, 2, ..., n.

    Guaranteed minimal. Complexity: O(2^n * |E|).
    Recommended only for small graphs (<= 15 nodes).
    """
    nodes = list(graph.nodes())
    n = len(nodes)

    if graph.number_of_edges() == 0:
        return set()

    for k in range(1, n + 1):
        for combo in itertools.combinations(nodes, k):
            cover_candidate = set(combo)
            if is_vertex_cover(graph, cover_candidate):
                return cover_candidate

    return set(nodes)


def _get_matching_lower_bound(edges: Set[Tuple[Any, Any]]) -> int:
    """
    Computes the size of a maximal matching (a set of pairwise non-adjacent edges).
    Since every independent edge requires at least one distinct vertex in any cover,
    the size of ANY matching provides a tight admissible lower bound on the remaining cover size.
    """
    matched_nodes = set()
    matching_size = 0
    for u, v in edges:
        if u not in matched_nodes and v not in matched_nodes:
            matched_nodes.add(u)
            matched_nodes.add(v)
            matching_size += 1
    return matching_size


def exact_vertex_cover_branch_and_bound(graph: nx.Graph) -> Set[Any]:
    """
    Calculates the exact minimum vertex cover using recursive branch-and-bound
    with edge reduction, maximal matching lower-bounding, and vertex-degree branching.

    Much faster than naive combinatorial enumeration while still guaranteeing
    100% mathematical optimality.
    """
    if graph.number_of_edges() == 0:
        return set()

    # Pre-process: normalize undirected edges as canonical frozensets
    all_edges = {tuple(sorted((u, v), key=str)) for u, v in graph.edges()}
    nodes = list(graph.nodes())

    # Initial upper bound can be obtained from greedy heuristic or all non-isolated nodes
    non_isolated = {node for node in nodes if graph.degree(node) > 0}
    best_cover = set(non_isolated)

    def search(
        current_cover: Set[Any],
        remaining_edges: Set[Tuple[Any, Any]],
        remaining_adj: dict,
    ):
        nonlocal best_cover

        # If all edges are covered, we found a valid cover
        if not remaining_edges:
            if len(current_cover) < len(best_cover):
                best_cover = set(current_cover)
            return

        # Prune if current size + lower bound >= best known cover
        lower_bound = _get_matching_lower_bound(remaining_edges)
        if len(current_cover) + lower_bound >= len(best_cover):
            return

        # Degree 1 Reduction: If any vertex has degree 1, it is always optimal to include
        # its neighbor rather than the vertex itself.
        deg1_vertex = None
        for v, neighbors in remaining_adj.items():
            if len(neighbors) == 1:
                deg1_vertex = v
                break

        if deg1_vertex is not None:
            neighbor = next(iter(remaining_adj[deg1_vertex]))
            # Mandatory branch: take neighbor
            new_cover = current_cover | {neighbor}
            # Remove all edges incident to neighbor
            removed_edges = {
                tuple(sorted((neighbor, nbr), key=str))
                for nbr in remaining_adj[neighbor]
            }
            new_remaining_edges = remaining_edges - removed_edges
            new_adj = {
                u: {w for w in nbrs if w != neighbor}
                for u, nbrs in remaining_adj.items()
                if u != neighbor and len(nbrs) > 0
            }
            search(new_cover, new_remaining_edges, new_adj)
            return

        # Choose the vertex with maximum remaining degree to branch on
        max_vertex = max(remaining_adj.keys(), key=lambda v: len(remaining_adj[v]))
        neighbors = set(remaining_adj[max_vertex])

        # Branch 1: Include max_vertex in cover
        branch1_cover = current_cover | {max_vertex}
        branch1_removed_edges = {
            tuple(sorted((max_vertex, nbr), key=str)) for nbr in neighbors
        }
        branch1_edges = remaining_edges - branch1_removed_edges
        branch1_adj = {
            u: {w for w in nbrs if w != max_vertex}
            for u, nbrs in remaining_adj.items()
            if u != max_vertex and len(nbrs) > 0
        }
        search(branch1_cover, branch1_edges, branch1_adj)

        # Branch 2: Exclude max_vertex -> MUST include all its neighbors in cover
        if len(current_cover) + len(neighbors) < len(best_cover):
            branch2_cover = current_cover | neighbors
            branch2_removed_edges = set()
            for nbr in neighbors:
                for w in remaining_adj.get(nbr, set()):
                    branch2_removed_edges.add(tuple(sorted((nbr, w), key=str)))
            branch2_edges = remaining_edges - branch2_removed_edges
            branch2_adj = {
                u: {w for w in nbrs if w not in neighbors}
                for u, nbrs in remaining_adj.items()
                if u not in neighbors and len(nbrs) > 0
            }
            search(branch2_cover, branch2_edges, branch2_adj)

    # Build initial adjacency list for active edges
    initial_adj = {node: set() for node in non_isolated}
    for u, v in all_edges:
        initial_adj[u].add(v)
        initial_adj[v].add(u)

    search(set(), all_edges, initial_adj)
    return best_cover


def solve_exact(
    graph: nx.Graph, method: str = "branch_and_bound"
) -> Tuple[Set[Any], float]:
    """
    Main entry point for exact minimum vertex cover solver.

    Args:
        graph: NetworkX graph.
        method: 'branch_and_bound' (recommended) or 'bruteforce'.

    Returns:
        (cover_set, elapsed_seconds)
    """
    start_time = time.perf_counter()
    if method == "bruteforce":
        cover = exact_vertex_cover_bruteforce(graph)
    elif method == "branch_and_bound":
        cover = exact_vertex_cover_branch_and_bound(graph)
    else:
        raise ValueError(f"Unknown exact method '{method}'")
    elapsed = time.perf_counter() - start_time
    return cover, elapsed
