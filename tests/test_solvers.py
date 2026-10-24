"""
test_solvers.py - Unit tests for Aegis exact and approximate vertex cover solvers.
"""

import pytest
import networkx as nx
from graph_utils import is_vertex_cover, get_handmade_graphs, generate_synthetic_graph
from exact_solver import (
    exact_vertex_cover_bruteforce,
    exact_vertex_cover_branch_and_bound,
    solve_exact,
)
from approx_solver import (
    approx_vertex_cover_2approx,
    approx_vertex_cover_greedy,
    solve_approx,
)


class TestSolvers:
    def test_empty_graph(self):
        G = nx.Graph()
        assert exact_vertex_cover_bruteforce(G) == set()
        assert exact_vertex_cover_branch_and_bound(G) == set()
        assert approx_vertex_cover_2approx(G) == set()
        assert approx_vertex_cover_greedy(G) == set()

    def test_single_edge(self):
        G = nx.Graph()
        G.add_edge("A", "B")

        exact_bb = exact_vertex_cover_branch_and_bound(G)
        assert len(exact_bb) == 1
        assert exact_bb in ({"A"}, {"B"})
        assert is_vertex_cover(G, exact_bb)

        approx_2 = approx_vertex_cover_2approx(G)
        assert len(approx_2) == 2
        assert approx_2 == {"A", "B"}
        assert is_vertex_cover(G, approx_2)

        approx_greedy = approx_vertex_cover_greedy(G)
        assert len(approx_greedy) == 1
        assert is_vertex_cover(G, approx_greedy)

    def test_handmade_graphs_exact_optimality(self):
        """
        Verify that both exact solvers find the known theoretical minimum vertex cover
        on all canonical hand-crafted graphs.
        """
        handmade = get_handmade_graphs()
        for name, (graph, expected_opt_size) in handmade.items():
            cover_bf = exact_vertex_cover_bruteforce(graph)
            cover_bb = exact_vertex_cover_branch_and_bound(graph)

            assert is_vertex_cover(
                graph, cover_bf
            ), f"BF failed cover test on {name}"
            assert is_vertex_cover(
                graph, cover_bb
            ), f"BB failed cover test on {name}"

            assert (
                len(cover_bf) == expected_opt_size
            ), f"BF size mismatch on {name}: expected {expected_opt_size}, got {len(cover_bf)}"
            assert (
                len(cover_bb) == expected_opt_size
            ), f"BB size mismatch on {name}: expected {expected_opt_size}, got {len(cover_bb)}"

    def test_approximation_bounds(self):
        """
        Verify that 2-approximation and greedy heuristics produce valid vertex covers
        and strictly adhere to |C| <= 2 * |OPT|.
        """
        handmade = get_handmade_graphs()
        for name, (graph, opt_size) in handmade.items():
            cover_2approx, _ = solve_approx(graph, method="2approx")
            cover_greedy, _ = solve_approx(graph, method="greedy")

            assert is_vertex_cover(
                graph, cover_2approx
            ), f"2-approx not a valid cover on {name}"
            assert is_vertex_cover(
                graph, cover_greedy
            ), f"Greedy not a valid cover on {name}"

            # Strict 2-approximation theoretical guarantee
            assert (
                len(cover_2approx) <= 2 * opt_size
            ), f"2-approx exceeded 2*OPT on {name}"

    def test_synthetic_graphs_consistency(self):
        """
        Verify on various random topologies that BB matches Bruteforce
        and approximation bounds hold.
        """
        for seed in [1, 2, 3]:
            G = generate_synthetic_graph("scale_free", num_nodes=12, seed=seed)

            exact_cover, _ = solve_exact(G, method="branch_and_bound")
            bf_cover, _ = solve_exact(G, method="bruteforce")

            assert is_vertex_cover(G, exact_cover)
            assert is_vertex_cover(G, bf_cover)
            assert len(exact_cover) == len(bf_cover)

            approx_cover, _ = solve_approx(G, method="2approx")
            greedy_cover, _ = solve_approx(G, method="greedy")

            assert is_vertex_cover(G, approx_cover)
            assert is_vertex_cover(G, greedy_cover)
            assert len(approx_cover) <= 2 * len(exact_cover)
