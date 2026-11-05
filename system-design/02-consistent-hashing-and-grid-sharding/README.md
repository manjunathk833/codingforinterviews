# 🔄 System Design Lab 02: Consistent Hashing Ring & Distributed Grid Sharding

**Domain:** Distributed Systems, Load Balancing & Test Execution Sharding  
**Target Role:** Senior / Staff SDET & Infrastructure Architect  
**Interactive Visualizer:** `arch-concurrency-isolation` (`http://127.0.0.1:8090`)

---

## 🧠 1. Mental Model & Architectural Context

1. **Why Modulo Sharding (`hash(key) % N`) Fails Under Auto-Scaling**:
   Suppose you shard 1,000 stateful test suites or cache keys across $N = 4$ worker nodes using `hash(key) % 4`. If 1 worker node crashes ($N$ drops from $4 \to 3$), **`hash(key) % 3` changes the target node for ~75% of all keys**, triggering a massive cache stampede and state reshuffle!
2. **Consistent Hashing Ring with Virtual Nodes (`vnodes`)**:
   - Map both **Worker Nodes** and **Test/Cache Keys** onto a $32$-bit circular ring $[0, 2^{32}-1]$.
   - Each physical node is assigned $V$ **Virtual Nodes** (`node_1#v0 .. node_1#v63`) around the ring to guarantee uniform load balancing (preventing hot spots).
   - To route a key $k$, compute `hash(k)` and binary-search (`bisect_left` in Python / `TreeMap.ceilingEntry` in Java) clockwise for the first virtual node on the ring.
   - **Minimal Disruption Invariant**: When 1 out of $N$ nodes leaves or joins, only $\approx \mathbf{1/N}$ ($\sim 25\%$ for 4 nodes) of keys move!

---

## 🧪 2. Running Verification

```bash
./run.sh test 02-consistent-hashing-and-grid-sharding
```

