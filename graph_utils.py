"""
graph_utils.py - Graph utilities, validation, generation, and visualization for Aegis.
"""

from typing import Set, Tuple, Dict, Any, Optional
import networkx as nx
import matplotlib.pyplot as plt


def is_vertex_cover(graph: nx.Graph, cover: Set[Any]) -> bool:
    """
    Validates whether the given subset of vertices forms a valid vertex cover for graph G.
    A set C is a vertex cover if for every edge (u, v) in G, either u in C or v in C.
    """
    for u, v in graph.edges():
        if u not in cover and v not in cover:
            return False
    return True


def get_handmade_graphs() -> Dict[str, Tuple[nx.Graph, int]]:
    """
    Returns a collection of small, well-understood graphs with their known
    minimum vertex cover size for baseline correctness verification.
    """
    graphs = {}

    # 1. Star Graph S_5 (Center connected to 4 leaves) -> Min cover = {0} (size 1)
    star = nx.star_graph(4)  # 5 nodes total: 0 is center, 1..4 leaves
    graphs["star_5"] = (star, 1)

    # 2. Path Graph P_4 (0 - 1 - 2 - 3) -> Min cover = {1, 2} (size 2)
    path = nx.path_graph(4)
    graphs["path_4"] = (path, 2)

    # 3. Cycle Graph C_5 (0 - 1 - 2 - 3 - 4 - 0) -> Min cover = ceil(5/2) = 3
    cycle = nx.cycle_graph(5)
    graphs["cycle_5"] = (cycle, 3)

    # 4. Complete Bipartite K_{2,3} -> Min cover = smaller partition (size 2)
    bipartite = nx.complete_bipartite_graph(2, 3)
    graphs["bipartite_2_3"] = (bipartite, 2)

    # 5. Triangle with tail: 0-1, 1-2, 2-0, 2-3 -> Min cover size 2 ({1, 2} or {0, 2})
    triangle_tail = nx.Graph()
    triangle_tail.add_edges_from([(0, 1), (1, 2), (2, 0), (2, 3)])
    graphs["triangle_tail"] = (triangle_tail, 2)

    # 6. Petersen Graph (10 nodes, 15 edges) -> Known min vertex cover size 6
    petersen = nx.petersen_graph()
    graphs["petersen"] = (petersen, 6)

    return graphs


def generate_synthetic_graph(
    graph_type: str = "scale_free",
    num_nodes: int = 20,
    seed: Optional[int] = 42,
    **kwargs: Any,
) -> nx.Graph:
    """
    Generates synthetic graphs simulating diverse network topologies.

    Available types:
      - 'scale_free' / 'barabasi_albert': Models internet router/device topologies with power-law hub degrees.
      - 'random' / 'erdos_renyi': Standard random network graph G(n, p).
      - 'enterprise': Hierarchical tree (Gateway router -> Distribution switches -> Access hosts).
      - 'star': Single core router/gateway with peripheral devices.
    """
    if num_nodes < 2:
        G = nx.Graph()
        if num_nodes == 1:
            G.add_node(0)
        return G

    if graph_type in ("scale_free", "barabasi_albert"):
        m = kwargs.get("m", max(1, min(2, num_nodes - 1)))
        G = nx.barabasi_albert_graph(n=num_nodes, m=m, seed=seed)

    elif graph_type in ("random", "erdos_renyi"):
        p = kwargs.get("p", min(1.0, 4.0 / num_nodes))
        G = nx.erdos_renyi_graph(n=num_nodes, p=p, seed=seed)
        # Ensure graph has edges if p was too sparse
        if G.number_of_edges() == 0 and num_nodes > 1:
            G.add_edge(0, 1)

    elif graph_type == "star":
        G = nx.star_graph(num_nodes - 1)

    elif graph_type == "enterprise":
        # Realistic enterprise topology:
        # Node 0: Core Gateway
        # Nodes 1..k: Department Switches
        # Remaining nodes: Workstations / IoT devices partitioned among switches
        G = nx.Graph()
        gateway = "Gateway-0"
        G.add_node(gateway, role="core_gateway")

        num_switches = max(1, min(4, (num_nodes - 1) // 3))
        switches = [f"Switch-{i+1}" for i in range(num_switches)]
        for sw in switches:
            G.add_node(sw, role="switch")
            G.add_edge(gateway, sw)

        # Workstations attached to switches
        workstation_idx = 1
        curr_nodes = 1 + num_switches
        while curr_nodes < num_nodes:
            target_switch = switches[(workstation_idx - 1) % num_switches]
            host_name = f"Host-{workstation_idx}"
            G.add_node(host_name, role="host")
            G.add_edge(target_switch, host_name)
            workstation_idx += 1
            curr_nodes += 1

        # Add occasional peer-to-peer or server links
        if num_nodes >= 6:
            nodes_list = list(G.nodes())
            G.add_edge(nodes_list[1], nodes_list[-1])

    else:
        raise ValueError(f"Unknown graph type '{graph_type}'")

    return G


def visualize_network_cover(
    graph: nx.Graph,
    cover: Set[Any],
    title: str = "Aegis Network Topology Vertex Cover",
    output_path: Optional[str] = None,
    show: bool = False,
) -> None:
    """
    Renders the graph with monitoring vertices (in the cover) highlighted in crimson
    and standard nodes in slate blue.
    """
    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(graph, seed=42)

    # Partition nodes
    cover_nodes = [node for node in graph.nodes() if node in cover]
    non_cover_nodes = [node for node in graph.nodes() if node not in cover]

    # Draw non-cover nodes
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=non_cover_nodes,
        node_color="#6BAED6",
        node_size=500,
        label="Monitored Link Endpoints",
    )

    # Draw cover nodes (monitors / IDS sensors)
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=cover_nodes,
        node_color="#DE2D26",
        node_size=750,
        label=f"Active Sensors / Cover Nodes ({len(cover_nodes)})",
    )

    # Draw edges
    nx.draw_networkx_edges(graph, pos, edge_color="#999999", width=1.5, alpha=0.8)

    # Draw labels
    nx.draw_networkx_labels(
        graph, pos, font_size=9, font_family="sans-serif", font_weight="bold"
    )

    plt.title(title, fontsize=14, fontweight="bold", pad=15)
    plt.legend(scatterpoints=1, loc="upper right")
    plt.axis("off")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()
