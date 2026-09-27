# CH-01: Custom Retry Analyzer with Exponential Backoff

- **Target Level**: Senior SDET / QA Architect (Google, Amazon, Meta)
- **Domain**: Test Reliability & Flakiness Management

---

## Interview Problem Statement

In large-scale microservice distributed testing, network hiccups and temporary cold-start delays cause test flakiness.

Your task is to implement a **Retry Engine** that:
1. Retries a failing action or test function up to a maximum number of attempts (`maxRetries`).
2. Applies **exponential backoff delay** between retries (e.g., initial delay $\times 2^{\text{attempt}}$).
3. Distinguishes between **retriable exceptions** (e.g., `TimeoutException`, `503 Service Unavailable`, `IOException`) and **non-retriable exceptions** (e.g., `AssertionError`, `400 Bad Request`). Non-retriable exceptions must fail immediately without wasting time retrying.
4. Returns the successful result or throws the final exception if all retries are exhausted.

---

## Target Complexities
- **Time Complexity**: $O(\text{attempts})$
- **Space Complexity**: $O(1)$
