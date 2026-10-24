"""
scan.py - Network scanning and topology reconstruction using nmap.
"""

import socket
import subprocess
from typing import List, Dict, Optional, Tuple, Any
import networkx as nx

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False


def get_default_gateway_ip() -> Optional[str]:
    """
    Attempts to determine the default gateway IP on Linux using /proc/net/route or `ip route`.
    """
    try:
        with open("/proc/net/route", "r") as f:
            for line in f.readlines()[1:]:
                fields = line.strip().split()
                # Interface, Destination, Gateway, Flags...
                if len(fields) >= 3 and fields[1] == "00000000":
                    gateway_hex = fields[2]
                    # Convert hex to IP
                    ip_parts = [
                        str(int(gateway_hex[i : i + 2], 16))
                        for i in (6, 4, 2, 0)
                    ]
                    return ".".join(ip_parts)
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout:
            parts = res.stdout.split()
            if "via" in parts:
                idx = parts.index("via")
                return parts[idx + 1]
    except Exception:
        pass

    return None


def get_local_subnet() -> str:
    """
    Infers the primary local IPv4 subnet if not explicitly specified.
    Falls back to '127.0.0.1/32' if no outward interface is found.
    """
    gw = get_default_gateway_ip()
    if gw and "." in gw:
        parts = gw.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        parts = local_ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return "127.0.0.1/32"


def scan_network_live(
    target_subnet: Optional[str] = None,
    arguments: str = "-sn -PR",
    timeout_sec: int = 30,
) -> List[Dict[str, Any]]:
    """
    Executes a real nmap scan to discover live hosts on the target subnet.

    Args:
        target_subnet: e.g. '192.168.1.0/24' (defaults to local subnet if None).
        arguments: nmap flags (default '-sn' for ping/ARP discovery).
        timeout_sec: scan timeout in seconds.

    Returns:
        List of discovered host metadata dicts.
    """
    if not NMAP_AVAILABLE:
        raise RuntimeError("python-nmap is not installed or unavailable.")

    if not target_subnet:
        target_subnet = get_local_subnet()

    scanner = nmap.PortScanner()
    print(f"[*] Scanning subnet '{target_subnet}' with nmap arguments '{arguments}'...")
    scanner.scan(hosts=target_subnet, arguments=arguments, timeout=timeout_sec)

    discovered_hosts = []
    for host in scanner.all_hosts():
        status = scanner[host].state()
        if status == "up":
            hostname = scanner[host].hostname() or host
            vendor = scanner[host].get("vendor", {})
            mac = scanner[host].get("addresses", {}).get("mac", "unknown")
            discovered_hosts.append({
                "ip": host,
                "hostname": hostname,
                "vendor": vendor,
                "mac": mac,
                "status": status,
            })

    return discovered_hosts


def generate_mock_network_hosts() -> List[Dict[str, Any]]:
    """
    Provides a realistic mock network scan result for offline environments,
    CI/CD testing, or non-root container environments.
    """
    return [
        {"ip": "192.168.1.1", "hostname": "Gateway-Router", "role": "gateway"},
        {"ip": "192.168.1.2", "hostname": "Core-Switch", "role": "switch"},
        {"ip": "192.168.1.10", "hostname": "FileServer-NAS", "role": "server"},
        {"ip": "192.168.1.15", "hostname": "Office-Printer", "role": "iot"},
        {"ip": "192.168.1.101", "hostname": "Workstation-A", "role": "host"},
        {"ip": "192.168.1.102", "hostname": "Workstation-B", "role": "host"},
        {"ip": "192.168.1.103", "hostname": "Workstation-C", "role": "host"},
        {"ip": "192.168.1.150", "hostname": "Security-Camera", "role": "iot"},
        {"ip": "192.168.1.200", "hostname": "Employee-Phone", "role": "mobile"},
        {"ip": "192.168.1.201", "hostname": "Guest-Laptop", "role": "mobile"},
    ]


def build_network_graph(
    hosts: List[Dict[str, Any]],
    topology_model: str = "hierarchical",
) -> nx.Graph:
    """
    Constructs an undirected NetworkX graph from discovered hosts.

    Topology Models:
      - 'hierarchical': Gateway is connected to switches/servers; clients connect to switches;
                        shared resources (printers, file servers) are connected to clients.
      - 'star': All hosts connect directly to the identified gateway router.
      - 'mesh': Full peer-to-peer mesh between all active hosts.
    """
    G = nx.Graph()

    if not hosts:
        return G

    # Add all hosts as nodes with attributes
    for host in hosts:
        ip = host["ip"]
        G.add_node(
            ip,
            hostname=host.get("hostname", ip),
            role=host.get("role", "host"),
        )

    # Determine gateway (prefer explicitly labeled, or ending in .1, or first host)
    gateway_ip = None
    for h in hosts:
        if h.get("role") == "gateway" or h["ip"].endswith(".1"):
            gateway_ip = h["ip"]
            break
    if not gateway_ip:
        gateway_ip = hosts[0]["ip"]

    all_ips = [h["ip"] for h in hosts]

    if topology_model == "star":
        for ip in all_ips:
            if ip != gateway_ip:
                G.add_edge(gateway_ip, ip)

    elif topology_model == "mesh":
        for i in range(len(all_ips)):
            for j in range(i + 1, len(all_ips)):
                G.add_edge(all_ips[i], all_ips[j])

    elif topology_model == "hierarchical":
        # Realistic corporate/home network hierarchy:
        # Gateway -> Infrastructure (switches, servers) -> Endpoints
        servers_and_printers = [
            h["ip"]
            for h in hosts
            if h.get("role") in ("server", "iot", "switch")
            or "server" in h.get("hostname", "").lower()
            or "printer" in h.get("hostname", "").lower()
        ]
        clients = [
            h["ip"]
            for h in hosts
            if h["ip"] != gateway_ip and h["ip"] not in servers_and_printers
        ]

        # Gateway connects to servers and infrastructure
        for s in servers_and_printers:
            if s != gateway_ip:
                G.add_edge(gateway_ip, s)

        # Clients connect to gateway for upstream access
        for c in clients:
            G.add_edge(gateway_ip, c)

        # Clients connect to shared resources (e.g. file server or printer)
        for s in servers_and_printers:
            for c in clients[: max(2, len(clients) // 2)]:
                G.add_edge(s, c)
    else:
        raise ValueError(f"Unknown topology model '{topology_model}'")

    return G
