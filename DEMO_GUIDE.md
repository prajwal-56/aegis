# 🛡️ Aegis: Professor Demo & Presentation Workflow

This guide provides a step-by-step presentation script and live terminal demonstration workflow for demonstrating **Aegis** to your course professor or lab external evaluator for **Design and Analysis of Algorithms (PCCST502)**.

---

## ⏱️ Quick Summary (30-Second Elevator Pitch)

> *"Good morning, Professor. My project is **Aegis**—a network defense optimization engine that solves the **optimal Intrusion Detection System (IDS) and firewall sensor placement problem** using graph algorithms.*
>
> *In cybersecurity, installing expensive monitoring sensors on every single device is cost-prohibitive. But because network traffic travels over links between two devices, monitoring either end of a cable inspects 100% of packets passing through it. Mathematically, this is Karp's NP-complete **Minimum Vertex Cover** problem.*
>
> *I built an engine that takes real Nmap network scans and synthetic topologies, solves them using an **exact Branch-and-Bound algorithm**, a **polynomial-time 2-Approximation algorithm**, and a **Greedy heuristic**, and visualizes the exact sensor placement while proving mathematical bounds."*

---

## 🎬 Live Demo Workflow (Step-by-Step)

Follow these 5 steps in order during your live demo.

---

### Step 1: Run the Core Solver on an Enterprise Network (1-2 minutes)

**Terminal Command:**
```bash
python3 main.py --preset enterprise --nodes 14 --visualize
```

#### What happens:
Aegis builds a 14-device enterprise tree (1 Core Gateway, 4 Departmental Switches, 9 Workstations), executes all three algorithms, prints the ASCII comparison table, and generates a visual network diagram.

#### What to tell the professor:
> *"Here, Aegis modeled a standard 14-device departmental network. Notice the output table:*
> *1. **The Exact Solver (Branch & Bound)** proved that the absolute minimum number of sensors needed is **4**—specifically `[Switch-1, Switch-2, Switch-3, Switch-4]`.*
> *2. By monitoring just those 4 switches, **100% of all traffic across all 14 devices is inspected**.*
> *3. This yields an immediate **71.4% reduction in sensor deployment costs** without creating a single blind spot.*
> *4. Notice the **2-Approximation** found a cover of size 8. In accordance with theoretical proofs, 8 is $\le 2 \times |OPT| = 8$, mathematically verifying the 2x upper bound."*

#### Visual to show:
Open the generated image:
```bash
xdg-open results/network_cover.png   # or open in your image viewer
```
* **🔴 Crimson Red Nodes:** The chosen monitoring devices (switches).
* **🔵 Slate Blue Nodes:** Normal workstations that don't need sensors because their links are already covered.

---

### Step 2: Demonstrate on a Realistic Multi-Tier Corporate LAN (1 minute)

**Terminal Command:**
```bash
python3 main.py --mock --visualize --output results/mock_network_cover.png
```

#### What happens:
Aegis loads a real-world office topology with heterogeneous device roles (Gateway Router, Core Switch, File Server/NAS, Office Printer, Workstations, Security Camera, and Employee Phones).

#### What to tell the professor:
> *"Next, I tested Aegis against a heterogeneous corporate LAN with 10 devices and 17 connections, including servers and IoT cameras.*
> *The exact solver found that placing sensors on only **3 devices** (`192.168.1.1` Gateway, and two distribution workstations) inspects every single link.*
> *The Greedy heuristic matched the exact optimal cover ($1.0\times |OPT|$) in just **25 microseconds**, demonstrating how greedy degree selection excels on real-world star-bus network structures."*

#### Visual to show:
```bash
xdg-open results/mock_network_cover.png
```

---

### Step 3: Run the Empirical Benchmark Suite (2 minutes)

**Terminal Command:**
```bash
python3 benchmark.py --min-nodes 6 --max-nodes 20 --step 2 --output results/benchmark_comparison.png
```

#### What happens:
The benchmark suite evaluates network sizes from $n = 6$ up to $20$ nodes, testing the runtime scaling and cover size across repeated randomized trials.

#### What to tell the professor:
> *"To prove the algorithmic theory from our DAA syllabus, I built an automated benchmark suite comparing the time complexity and approximation ratios across increasing network sizes.*
> *Let's look at the generated chart."*

#### Visual to show:
```bash
xdg-open results/benchmark_comparison.png
```

#### Key points to explain from the chart:
1. **Left Plot (Runtime Scaling - Log Scale):**
   * The red line (Exact Branch-and-Bound) curves sharply upward, illustrating why exponential algorithms hit a brick wall on massive networks.
   * The blue and green lines (2-Approximation and Greedy) remain nearly flat, running in microseconds—proving polynomial efficiency $O(|E|)$.
2. **Right Plot (Solution Quality Bounds):**
   * The dashed black line represents the theoretical ceiling ($2 \times |OPT|$).
   * Notice the blue curve (2-Approximation) stays strictly underneath that ceiling for every graph size.
   * Notice the green curve (Greedy) closely tracks the red optimal curve $|OPT|$, confirming its empirical effectiveness.

---

### Step 4: Show Automated Pytest Verification Suite (30 seconds)

**Terminal Command:**
```bash
pytest -v
```

#### What happens:
Pytest runs all 10 unit and integration tests across hand-crafted canonical graphs and topology models.

#### What to tell the professor:
> *"I implemented a test suite with 10 automated test cases verifying correctness on canonical benchmark graphs from graph theory: Star graphs ($S_5$), Path graphs ($P_4$), Cycle graphs ($C_5$), Bipartite graphs ($K_{2,3}$), and the Petersen Graph.*
> *All 10 tests execute and pass in under half a second, ensuring mathematical correctness and zero regressions."*

---

### Step 5: (Optional Bonus) Live Nmap Subnet Scan (1 minute)

**Terminal Command:**
```bash
python3 main.py --scan auto --visualize
```

#### What to tell the professor:
> *"Aegis isn't just a theoretical simulation—it actively interfaces with the operating system. By passing `--scan`, it queries `/proc/net/route` to locate the local gateway, executes an active ARP/ping discovery scan via Nmap, extracts live IPs and hostnames, and reconstructs the real network topology for sensor placement."*

---

## 🧠 Anticipated Professor Questions & Model Answers

### Q1: *"Why is sensor placement modeled as Vertex Cover and not Edge Cover?"*
* **Answer:** An **Edge Cover** selects links to cover all vertices. That would mean choosing cables. But we don't install software on cables; we install software on **machines** (vertices). To ensure every cable (edge) is inspected by at least one machine, we must select vertices such that every edge touches at least one selected vertex. That is the exact mathematical definition of **Vertex Cover**.

---

### Q2: *"Why do we need a 2-approximation if your Branch-and-Bound solver is exact?"*
* **Answer:** Because Vertex Cover is **NP-complete**. While our Branch-and-Bound algorithm prunes massive subtrees (solving up to 30 nodes in milliseconds), its worst-case complexity is still exponential ($O(1.465^n)$). On an enterprise network with 500 or 1,000 devices, an exact solver cannot finish in our lifetime. The 2-approximation runs in linear time $O(|E|)$ and mathematically guarantees that the solution will never be worse than twice the optimal.

---

### Q3: *"How does the mathematical proof for the 2-approximation work?"*
* **Answer:** 
  1. Our algorithm repeatedly picks an uncovered edge $(u, v)$ and adds **both** endpoints to the cover, then removes all touching edges.
  2. The edges chosen form a **matching** $M$ (edges sharing no common endpoints).
  3. Any valid cover—including the optimal cover $C^*$—must contain at least one vertex from each independent edge in $M$. Therefore, $|C^*| \ge |M|$.
  4. Since our algorithm took 2 vertices for every edge in $M$, our cover size is $|C| = 2 \cdot |M|$.
  5. Combining these gives $|C| = 2 \cdot |M| \le 2 \cdot |C^*|$.

---

### Q4: *"What is the 'Subnet Clique Trap' and how did you solve it?"*
* **Answer:** In standard networking, naive scanners assume every device on a `/24` subnet can communicate with every other device, forming a complete graph (clique $K_n$). On $K_n$, the minimum vertex cover is mathematically trivial: exactly $n - 1$ devices (every machine except one). That provides no insight. 
* Aegis avoids this by analyzing routing tables to identify the **default gateway**, modeling switches and server clusters, and reconstructing a realistic hierarchical tree structure rather than a naive mesh.

---

### Q5: *"How does your Branch-and-Bound solver achieve $O(1.465^n)$ instead of $O(2^n)$?"*
* **Answer:** It uses three optimizations:
  1. **Matching Lower Bound:** Computes a maximal matching $M$ on remaining edges. If $\text{current cover} + |M| \ge \text{best known cover}$, it immediately prunes the branch.
  2. **Degree-1 Reduction:** If a device has only 1 connection, choosing its neighbor is always optimal or tied, eliminating redundant branches.
  3. **Max-Degree Branching:** Branching on the highest-degree vertex $v$ creates two asymmetric branches: Branch 1 takes $v$, while Branch 2 excludes $v$ and forces **all** its neighbors $N(v)$ into the cover. This yields the recurrence $T(n) \le T(n-1) + T(n-3)$, which solves to $O(1.465^n)$.

---

## 📋 Command Cheat Sheet

| Demonstration Target | Terminal Command |
|---|---|
| **Enterprise Network (14 nodes)** | `python3 main.py --preset enterprise --nodes 14 --visualize` |
| **Corporate LAN (Heterogeneous)** | `python3 main.py --mock --visualize` |
| **Live Local Network Scan** | `python3 main.py --scan auto --visualize` |
| **Comparative Benchmark Suite** | `python3 benchmark.py --min-nodes 6 --max-nodes 20 --step 2` |
| **Unit Test Suite (10 tests)** | `pytest -v` |
| **View Output Network Image** | `xdg-open results/network_cover.png` |
| **View Benchmark Scaling Plot** | `xdg-open results/benchmark_comparison.png` |
| **Official 20-Page Project Report** | `libreoffice Aegis_Project_Report.docx` (or open `.pdf`) |
