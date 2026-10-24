"""
test_scan.py - Unit tests for network scanning and topology construction.
"""

import pytest
import networkx as nx
from scan import (
    generate_mock_network_hosts,
    build_network_graph,
    get_default_gateway_ip,
    get_local_subnet,
)
from exact_solver import solve_exact
from approx_solver import solve_approx
from graph_utils import is_vertex_cover


class TestScan:
    def test_mock_hosts_generation(self):
        hosts = generate_mock_network_hosts()
        assert len(hosts) == 10
        assert any(h["role"] == "gateway" for h in hosts)

    def test_star_topology_construction(self):
        hosts = generate_mock_network_hosts()
        G = build_network_graph(hosts, topology_model="star")
        assert G.number_of_nodes() == 10
        assert G.number_of_edges() == 9
        # Center is the gateway, so min vertex cover size must be 1!
        cover, _ = solve_exact(G)
        assert len(cover) == 1
        assert "192.168.1.1" in cover

    def test_hierarchical_topology_construction(self):
        hosts = generate_mock_network_hosts()
        G = build_network_graph(hosts, topology_model="hierarchical")
        assert G.number_of_nodes() == 10
        assert G.number_of_edges() > 9

        cover_exact, _ = solve_exact(G)
        assert is_vertex_cover(G, cover_exact)

        cover_approx, _ = solve_approx(G, method="2approx")
        assert is_vertex_cover(G, cover_approx)
        assert len(cover_approx) <= 2 * len(cover_exact)

    def test_mesh_topology_construction(self):
        hosts = generate_mock_network_hosts()[:5]  # 5 nodes -> K_5 has 10 edges
        G = build_network_graph(hosts, topology_model="mesh")
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 10

        cover_exact, _ = solve_exact(G)
        assert len(cover_exact) == 4  # Complete graph K_n has min cover n-1
        assert is_vertex_cover(G, cover_exact)

    def test_subnet_inference(self):
        subnet = get_local_subnet()
        assert isinstance(subnet, str)
        assert "/" in subnet
