# CH-02: Deep JSON Payload Diff Engine

- **Target Level**: Senior SDET / Microservices QE (Meta, Google, Uber)
- **Domain**: Contract & Regression Testing in Distributed Systems

---

## Interview Problem Statement

In API test automation, comparing large, deeply nested microservice JSON responses often fails with standard string or naive dictionary equality because:
1. Dynamic fields change per run (e.g. `timestamp`, `traceId`, `uuid`).
2. JSON array elements may arrive in arbitrary order unless ordered by the database.
3. Floating point values may have micro-rounding differences.

Your task is to implement a **Deep JSON Diff Engine** that compares two parsed JSON structures (nested maps, lists, primitives) and returns a list of human-readable discrepancies:
1. Detects **Missing Keys** (present in expected, absent in actual).
2. Detects **Unexpected Keys** (absent in expected, present in actual).
3. Detects **Value Mismatches** at exact nested paths (e.g. `user.address.zipcode: expected 560001, got 560002`).
4. Supports an **ignored paths set** (e.g. `["timestamp", "id"]`) that skips comparison for dynamic fields.

---

## Target Complexities
- **Time Complexity**: $O(N)$ where $N$ is total nodes in the JSON tree
- **Space Complexity**: $O(D)$ where $D$ is max depth of recursion
