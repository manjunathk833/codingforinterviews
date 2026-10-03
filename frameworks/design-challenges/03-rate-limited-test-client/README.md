# CH-03: Thread-Safe Rate-Limited Test Client (Token Bucket)

- **Target Level**: Staff SDET / Performance Architect (Google, Netflix, Amazon)
- **Domain**: High-Throughput Load Testing & API Throttling

---

## Interview Problem Statement
When running massive parallel test suites against rate-limited microservices (e.g., maximum 10 requests per second with burst capacity of 10), sending unmetered requests triggers `429 Too Many Requests`.

Your task is to implement a **Thread-Safe Rate Limiter** using the **Token Bucket Algorithm**:
1. Initialized with `capacity` (max burst tokens) and `refillRatePerSecond` (tokens added per second).
2. The method `acquire()` or `tryAcquire(tokens)` blocks or returns boolean indicating whether the requested tokens could be consumed.
3. Automatically replenishes tokens based on elapsed wall-clock time without spawning a background busy-wait thread.
4. Thread-safe under concurrent multi-threaded test access.

---

## Target Complexities
- **Time Complexity**: $O(1)$ per token acquisition request
- **Space Complexity**: $O(1)$ memory
