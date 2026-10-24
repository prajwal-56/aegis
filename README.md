# 🛡️ Aegis: Network Topology Minimum Vertex Cover Engine

Aegis is a network defense optimization tool that computes the **Minimum Vertex Cover (MVC)** on real and synthetic computer network topologies.

By framing optimal IDS/sensor placement, packet monitoring, and firewall node selection as a Vertex Cover problem, Aegis demonstrates how combinatorial optimization can dramatically reduce monitoring overhead while guaranteeing 100% link coverage across the entire network.

---

## 🚀 Key Features

1. **Algorithms & Solvers:**
   - **Exact Solver:** Branch-and-bound recursive search with vertex reduction and degree heuristic branching (guarantees the absolute minimal vertex cover).
   - **2-Approximation Solver:** Classic polynomial-time maximal matching algorithm (guarantees $|C| \le 2 \times |C^*|$ in $O(|E|)$ time).
   - **Greedy Degree Solver:** High-performance degree-based heuristic that repeatedly selects highest unmonitored degree nodes ($O(\log \Delta)$ factor).
2. **Real Network Ingestion:**
   - Active host & topology discovery using `nmap`.
   - Subnet topology reconstruction with gateway-centric star and mesh routing models.
   - Built-in synthetic topology presets (Barabási–Albert scale-free, Erdős–Rényi random, Star/Enterprise tree) for offline benchmarking.
3. **Benchmarking & Analysis:**
   - Runtime scaling comparison (exponential curve vs. near-flat polynomial curve).
   - Approximation ratio verification across varying graph sizes.
   - Automated visualization of graph topologies with highlighted monitoring nodes.

---

## 📦 Installation

Ensure `nmap` is installed on your system:
```bash
# Debian / Ubuntu / Mint
sudo apt install nmap

# Arch Linux / Manjaro
sudo pacman -S nmap

# Fedora / RHEL
sudo dnf install nmap
```

Clone the repository and set up the Python environment:
```bash
git clone https://github.com/prajwal-56/aegis.git
cd aegis

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Usage

### 1. Run the CLI
```bash
python3 main.py --help
```

### 2. Solve on a Synthetic Topology
```bash
# Run on an enterprise star-tree network with 20 devices
python3 main.py --preset enterprise --nodes 20 --visualize
```

### 3. Scan & Solve on Real Network
```bash
# Scan local subnet (e.g. 192.168.1.0/24)
python3 main.py --scan 192.168.1.0/24 --visualize
```

### 4. Run Benchmarks & Generate Plots
```bash
python3 benchmark.py --max-nodes 30 --step 2 --output results/benchmark.png
```

---

## 📊 Project Architecture

```
aegis/
├── graph_utils.py      # Graph generation, topology builders, graph drawing
├── exact_solver.py     # Branch-and-bound exact minimum vertex cover solver
├── approx_solver.py    # 2-approximation (maximal matching) & greedy heuristics
├── scan.py              # nmap active scanner & network topology reconstructor
├── benchmark.py         # Empirical time and approximation ratio benchmark suite
├── main.py              # Unified CLI interface
├── tests/               # Unit and regression test suite
└── results/             # Generated charts and network plots
```

---

## 📜 License
MIT License.
