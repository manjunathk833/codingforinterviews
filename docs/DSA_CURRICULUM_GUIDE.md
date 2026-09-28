# DSA Curriculum Guide & Algorithmic Pattern Manual

This guide breaks down the **13 core algorithmic patterns** required for MAANG coding rounds, explaining pattern triggers, complexity trade-offs, common edge cases, and code templates in both Java and Python.

---

## 🧭 The 13 Core Algorithmic Patterns

### 1. Arrays & Hashing
- **Recognition Triggers**: Finding duplicates, checking anagrams, subarray sums, frequency counting, finding pairs summing to a target.
- **Mental Model**: Trading $O(N)$ space using a `HashMap` or `HashSet` to achieve $O(1)$ lookup time, replacing a naive $O(N^2)$ nested loop.
- **Key Techniques**:
  - Hash Map value-to-index mapping (Two Sum).
  - Prefix Sum array / map (Subarray Sum Equals K).
  - Frequency array of size 26 for ASCII lowercase strings (Valid Anagram).
- **Time/Space Trade-off**: Time $O(N)$, Space $O(N)$ or $O(1)$ for fixed-size alphabet.
- **Pitfalls**: Negative numbers in prefix sums (cannot use sliding window), hash collision overhead.

---

### 2. Two Pointers
- **Recognition Triggers**: Sorted arrays, palindromes, pair comparisons, trapping water, partitioning.
- **Mental Model**: Squeezing inward from both ends (`left`, `right`) or moving in the same direction (fast/slow).
- **Key Techniques**:
  - Inward scan (`left++`, `right--`) on sorted arrays (3Sum, Two Sum II, Container With Most Water).
  - Fast and slow pointers (remove duplicates in-place).
- **Time/Space Trade-off**: Time $O(N)$ (or $O(N \log N)$ if sorting is needed), Space $O(1)$.
- **Pitfalls**: Forgetting to skip duplicate elements in 3Sum resulting in non-unique triplets.

---

### 3. Sliding Window
- **Recognition Triggers**: Contiguous subarrays or substrings meeting a condition (max sum, longest substring without repeats, minimum window).
- **Mental Model**: An expandable and contractible window `[left, right]`. Expand `right` to include elements until the condition is violated; then shrink `left` until the condition is restored.
- **Key Techniques**:
  - Dynamic window: `right` expands every iteration; `left` shrinks while condition holds/fails.
  - Fixed-size window: Window length is always $K$.
- **Time/Space Trade-off**: Time $O(N)$ (each element is visited at most twice: once by `right`, once by `left`), Space $O(K)$ where $K$ is distinct elements in window.
- **Pitfalls**: Resetting the window unnecessarily; not tracking the valid character count in Minimum Window Substring.

---

### 4. Stack & Monotonic Queue
- **Recognition Triggers**: Matching parentheses/tags, finding the Next Greater Element, histograms, nested expressions.
- **Mental Model**: Last-In-First-Out (LIFO). Elements in a **Monotonic Stack** maintain strict increasing or decreasing order. When a new element violates the order, pop elements and resolve their span/range.
- **Key Techniques**:
  - Monotonic Decreasing Stack: Finds Next Greater Element (Daily Temperatures).
  - Stack with Min Tracking: Auxiliary stack or pair storing `(val, current_min)`.
- **Time/Space Trade-off**: Time $O(N)$ (each element pushed/popped at most once), Space $O(N)$.
- **Pitfalls**: Off-by-one indices when calculating histogram rectangle width (`i - stack.peek() - 1`).

---

### 5. Binary Search & Search Space Reduction
- **Recognition Triggers**: Sorted arrays, rotated sorted arrays, finding boundaries ("Find the minimum $X$ such that condition $P(X)$ holds").
- **Mental Model**: Halving the search space at each step. Can be applied to arrays OR over answer ranges (e.g. eating speed in Koko Eating Bananas).
- **Key Techniques**:
  - `mid = left + (right - left) / 2` to avoid integer overflow in Java.
  - Rotated array: Determine which half (`[left..mid]` or `[mid..right]`) is strictly sorted.
- **Time/Space Trade-off**: Time $O(\log N)$, Space $O(1)$.
- **Pitfalls**: Infinite loops caused by `left = mid` instead of `left = mid + 1`.

---

### 6. Linked Lists
- **Recognition Triggers**: Reversing sequences in-place, merging sorted streams, cycle detection, reordering nodes.
- **Mental Model**: Node pointers. Always consider using a `dummy` head node to simplify edge cases where the head changes.
- **Key Techniques**:
  - In-place reversal: `prev = null; curr = head; while(curr != null) { next = curr.next; curr.next = prev; prev = curr; curr = next; }`.
  - Fast & Slow pointers (Floyd's Cycle Detection, finding middle node).
- **Time/Space Trade-off**: Time $O(N)$, Space $O(1)$ auxiliary.
- **Pitfalls**: Losing the `next` pointer before reassignment; null pointer exceptions on `fast.next.next`.

---

### 7. Trees & Binary Search Trees (BST)
- **Recognition Triggers**: Hierarchical relationships, path sums, Lowest Common Ancestor (LCA), serialization, BST validation.
- **Mental Model**: Recursion (DFS) or Queue (BFS). A tree is an acyclic connected graph where each sub-problem is identical on subtrees.
- **Key Techniques**:
  - DFS: Pre-order, In-order (yields sorted order in BST), Post-order (bottom-up aggregation).
  - BFS (Level Order): Queue with `size = queue.size()` per level.
  - Tree DP / Max Path Sum: Return the single-branch max to parent while updating global maximum through root.
- **Time/Space Trade-off**: Time $O(N)$, Space $O(H)$ recursion stack ($H = \log N$ balanced, $H = N$ skewed).
- **Pitfalls**: BST validation must check against upper and lower bounds (`(min, max)`), not just immediate children.

---

### 8. Heaps & Priority Queues
- **Recognition Triggers**: "Top K", "Kth largest/smallest", continuous median of a stream, task scheduling.
- **Mental Model**: Complete binary tree maintaining heap property. Min-Heap of size $K$ preserves the top $K$ largest elements.
- **Key Techniques**:
  - Two Heaps: Max-Heap for lower half, Min-Heap for upper half (Find Median from Data Stream).
  - Java: `PriorityQueue<Integer> pq = new PriorityQueue<>((a, b) -> b - a);`
  - Python: `heapq.heappush(heap, val)`, `heapq.heappop(heap)`. (Python is min-heap by default; invert signs for max-heap).
- **Time/Space Trade-off**: Time $O(N \log K)$, Space $O(K)$.
- **Pitfalls**: Integer underflow in Java comparator subtraction `(a, b) -> a - b`. Use `Integer.compare(a, b)`.

---

### 9. Backtracking & Combinatorics
- **Recognition Triggers**: Finding all valid combinations, permutations, subsets, partitionings, solving Sudoku / N-Queens.
- **Mental Model**: Depth-First Search on a state-space decision tree. **Choose $\to$ Explore $\to$ Unchoose (Backtrack)**.
- **Key Techniques**:
  - Subsets: At each element, branch into "include" or "exclude".
  - Permutations: Track `used[]` boolean array or swap in-place.
  - Combination Sum: Can reuse same element $\to$ pass current index `i` rather than `i + 1`.
- **Time/Space Trade-off**: Time $O(2^N)$ or $O(N!)$, Space $O(N)$ recursion depth.
- **Pitfalls**: Forgetting to create a deep copy of the path when adding to results list (`new ArrayList<>(currentPath)` / `current_path[:]`).

---

### 10. Graphs (BFS, DFS, Union-Find)
- **Recognition Triggers**: Grids with connected components, cycle detection, topological dependencies (Course Schedule), shortest path in unweighted graphs.
- **Mental Model**: Nodes and edges. Graph traversal requires a `visited` set to prevent infinite loops from cycles.
- **Key Techniques**:
  - Flood Fill / Island Count: Traverse in 4 cardinal directions `[(0,1), (0,-1), (1,0), (-1,0)]`.
  - Topological Sort: Kahn's algorithm (indegree array + queue) or DFS with 3-color states (0=unvisited, 1=visiting, 2=visited).
  - Disjoint Set Union (DSU / Union-Find) with path compression and union by rank.
- **Time/Space Trade-off**: Time $O(V + E)$, Space $O(V + E)$.
- **Pitfalls**: Matrix out-of-bounds indices; not marking cell visited immediately upon enqueueing in BFS.

---

### 11. Dynamic Programming (1D & 2D)
- **Recognition Triggers**: Optimization ("min cost", "max profit", "count unique ways"), overlapping subproblems, optimal substructure.
- **Mental Model**:
  1. Define state `dp[i]` or `dp[i][j]` precisely in words.
  2. Formulate recurrence relation transitioning from smaller subproblems.
  3. Identify base cases.
  4. Space optimization: If `dp[i]` only depends on `dp[i-1]` and `dp[i-2]`, reduce from $O(N)$ space to $O(1)$ variables.
- **Time/Space Trade-off**: Time $O(N)$ or $O(M \times N)$, Space $O(1)$ to $O(M \times N)$.
- **Pitfalls**: Off-by-one in DP table sizing (size $N+1$ vs $N$).

---

### 12. Greedy & Intervals
- **Recognition Triggers**: Merging intervals, scheduling meetings, local choices leading to global optimum.
- **Mental Model**: Sort intervals by start time (or end time for activity selection), then iterate and resolve overlaps greedily.
- **Key Techniques**:
  - Merge Intervals: If `curr.start <= prev.end`, merge by setting `prev.end = max(prev.end, curr.end)`.
  - Meeting Rooms II: Min-heap of end times or two pointer scan of sorted starts and ends.
- **Time/Space Trade-off**: Time $O(N \log N)$ (sorting dominated), Space $O(N)$ or $O(1)$.
- **Pitfalls**: Sorting by start time when end time was required (e.g., Non-overlapping intervals requires sorting by end time).

---

### 13. Design & Concurrency
- **Recognition Triggers**: LRU/LFU Cache, Prefix Tree (Trie), Thread-safe bounded queue.
- **Mental Model**: Combining multiple data structures (e.g. `HashMap` + Doubly Linked List for $O(1)$ LRU Cache).
- **Key Techniques**:
  - Trie: Node with array `children[26]` and boolean `isEndOfWord`.
  - Thread-safe Queue: `ReentrantLock` with `notFull` and `notEmpty` conditions.
- **Time/Space Trade-off**: Operations $O(1)$ or $O(\text{word length})$, Space proportional to capacity.
