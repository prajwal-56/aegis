# Aegis — Build Plan

## 1. Overview

Aegis is built in **four layers**, each one working before you move to the next:

```
Layer 4: Interface        (CLI output / simple visualization)
Layer 3: Real Data         (nmap scan → graph)
Layer 2: Analysis          (timing, comparison, charts)
Layer 1: Core Algorithms   (exact solver + approximate solver)
```

---

## 2. Tools & Setup

| Tool | Purpose |
|---|---|
| **Python 3** | Everything is written in Python — fast to iterate, has every library you need |
| **NetworkX** | Represents graphs (nodes + edges), has built-in drawing, easy to query "neighbors of a node" etc. |
| **Matplotlib** | Draws the graph visually and plots the runtime comparison chart |
| **`nmap`** + **`python-nmap`** | Scans your real network and gives you a list of live hosts |
| **Linux environment** | You already work in Linux — `nmap` runs natively, no extra setup |
| **`time` module (Python built-in)** | Measures how long each solver takes, for your performance comparison |

Setup is one `pip install networkx matplotlib python-nmap` and making sure `nmap` itself is installed (`sudo apt install nmap` on most Linux distros).

Project folder structure, roughly:
```
aegis/
├── graph_utils.py      # load/build graphs, convert nmap output → graph
├── exact_solver.py     # backtracking minimum vertex cover
├── approx_solver.py    # 2-approximation vertex cover
├── benchmark.py         # times both solvers across graph sizes, plots results
├── scan.py              # runs nmap, builds a graph from real network
├── main.py              # ties it together, CLI entry point
└── results/              # saved charts, output graphs
```

---

## 3. How Each Part Works

### 3.1 Graph representation
A network is just a **graph**: devices are *nodes*, connections are *edges*. In code, this is literally:
```python
import networkx as nx
G = nx.Graph()
G.add_edge("DeviceA", "DeviceB")
```
NetworkX stores and lets you query this instantly — no need to build your own graph data structure from scratch.

### 3.2 Exact Solver (Backtracking)
**Goal:** find the smallest possible set of vertices that touches every edge — guaranteed correct.

**How it works:** Try increasing cover sizes (1 device, then 2, then 3...). For each size, try combinations of that many vertices and check: *does this set touch every edge?* The moment you find a working set, that's your answer — since you tried smaller sizes first, it's guaranteed minimal. Backtracking means you abandon a partial combination early the moment it can't possibly work, instead of blindly trying everything.

**Why it's slow:** for a network of `n` devices, the number of possible subsets to check grows like `2^n` — this is the "exponential blowup" your abstract talks about. Fine for 10–15 devices, unusable for 100.

### 3.3 Approximate Solver (2-Approximation)
**Goal:** find a *good* cover, fast — not necessarily the smallest.

**How it works:** Pick any edge that isn't covered yet. Add *both* its endpoints to your cover set (even though technically you might only need one — this is the trick that makes the math work out). Remove every edge now touched by those two. Repeat until no edges remain.

**Why it's fast:** this is a simple loop — no searching, no trying combinations. Runs in time proportional to the number of edges, not exponential.

**Why it's "2-approximation":** it's mathematically provable that this method never picks more than *twice* as many devices as the true minimum. You don't need to prove this yourself — just cite it and demonstrate it empirically in your results.

### 3.4 Benchmark & Comparison
Generate random graphs of increasing size (10, 20, 30... nodes), run both solvers on each, record:
- Time taken
- Size of the cover found

Plot this with Matplotlib: one line showing the exact solver's time curving sharply upward (exponential), one line showing the approximate solver staying nearly flat. This chart *is* your core piece of evidence for the whole project.

### 3.5 Real Network Data
`nmap` scans your network and tells you what's alive:
```python
import nmap
scanner = nmap.PortScanner()
scanner.scan('192.168.1.0/24', arguments='-sn')  # -sn = ping scan, just find hosts
hosts = scanner.all_hosts()
```
This gives you your **nodes**. For **edges** (connections), the simplest honest approach: assume every device on the same subnet can reach every other device (common for home Wi-Fi) — this is a reasonable, statable simplification for your project, not a flaw you need to hide. You build the graph from this, then run both solvers on it exactly like you did on the fake graphs.

### 3.6 Output / Interface
Once the logic works, the simplest finish: a CLI script that prints something like:
```
Exact solver:      3 devices required [Router, Laptop-A, Phone-B]   (took 0.004s)
Approx solver:      4 devices required [Router, Laptop-A, Printer, Phone-B]  (took 0.0001s)
```
plus a saved image showing the network graph with the chosen devices highlighted in red, and the timing chart from 3.4.

---

## 4. Build Order (step-by-step)

1. **Exact solver on tiny hand-made graphs** (5–8 nodes you draw yourself) — confirm correctness by checking answers by hand.
2. **Approximate solver on the same graphs** — compare its output size against the exact answer.
3. **Benchmark script** — random graphs, increasing size, timing both, first chart.
4. **nmap scan script** — get real hosts, build the real graph.
5. **Run both solvers on the real graph** — your actual "here's what Aegis found on my network" result.
6. **Wrap in CLI + visualization** — polish last, once everything underneath works.

---
