#!/usr/bin/env python3
"""
Architecture Kata 01: Dynamic Tenant Key Partitioning
Candidate Workspace — Implement your solution below!

Goal:
1. Make 32 parallel worker threads succeed simultaneously when booking Seat 1A.
2. Eliminate all HTTP 409 Conflict race conditions without clearing databases.
"""

import concurrent.futures
import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error
import uuid

# Setup repo root path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from apps.aerocart.server import ThreadedHTTPServer, AeroCartHandler

TEST_PORT = 8993
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def start_test_server():
    server = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), AeroCartHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.15)
    return server


# ==============================================================================
# ✍️ CANDIDATE IMPLEMENTATION AREA
# ==============================================================================
def run_isolated_worker(worker_id: int) -> dict:
    """
    TODO: Implement Dynamic Tenant Isolation for this worker thread.

    Requirements:
    1. Generate an ephemeral, cryptographically unique tenant identifier for this execution.
    2. Construct the booking payload for Flight 'AI-202' and Seat '1A'.
    3. Inject the tenant identifier into the request headers via 'X-Test-Tenant-ID'.
    4. Execute the HTTP POST request to f"{BASE_URL}/api/v1/orders".
    5. Return a dictionary containing at least:
       {"worker_id": worker_id, "status": resp.status, "data": response_json}
    """
    # --------------------------------------------------------------------------
    # WRITE YOUR CODE HERE:
    # --------------------------------------------------------------------------
    raise NotImplementedError("Candidate must implement run_isolated_worker() with dynamic tenant isolation!")


# ==============================================================================
# 🧪 TEST HARNESS & VERIFICATION RUNNER
# ==============================================================================
def main():
    print("=" * 70)
    print("🛠️  VERIFYING CANDIDATE IMPLEMENTATION: 32 Parallel Isolated Workers")
    print("=" * 70)

    server = start_test_server()
    num_workers = 32

    try:
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(run_isolated_worker, i) for i in range(1, num_workers + 1)]
            results = [f.result() for f in futures]
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        passed = [r for r in results if r.get("status") == 201]
        failed = [r for r in results if r.get("status") != 201]

        print(f"\n📊 EXECUTION RESULTS across {num_workers} parallel threads ({elapsed_ms:.1f}ms):")
        print(f"   ✓ Passed (201 Created): {len(passed)} / {num_workers}")
        print(f"   ✗ Failed: {len(failed)} / {num_workers}")

        if len(passed) == num_workers and len(failed) == 0:
            print("\n" + "=" * 70)
            print("🎉 CONGRATULATIONS! All 32 parallel threads passed with 0 collisions!")
            print("   You have successfully mastered Dynamic Tenant Key Partitioning.")
            print("   Now invoke /interviewer to evaluate your architecture!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print(f"⚠️  VERIFICATION FAILED: Expected 32 passed, got {len(passed)}. Review errors above.")
            print("=" * 70)
            sys.exit(1)

    except NotImplementedError as e:
        print(f"\n⏳ SKELETON DETECTED: {e}")
        print("👉 Open frameworks/sdet-system-design/01-distributed-concurrency-isolation/solution.py and implement run_isolated_worker()!")
        sys.exit(2)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
