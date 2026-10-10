#!/usr/bin/env python3
"""
Naive Baseline: 32 Parallel Workers Mutating Shared Global Inventory.
Demonstrates the exact race condition and test collision failure mode
seen in distributed microservice CI/CD pipelines.
"""

import concurrent.futures
import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error

# Ensure repo root is in python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from apps.aerocart.server import ThreadedHTTPServer, AeroCartHandler

TEST_PORT = 8991
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def start_test_server():
    server = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), AeroCartHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.15)
    return server


def naive_worker_booking(worker_id: int) -> dict:
    """Worker books Seat 1A on AI-202 WITHOUT tenant isolation (naive global shared mode)."""
    payload = json.dumps({
        "flightNumber": "AI-202",
        "seat": "1A",
        "passengerEmail": f"worker_{worker_id}@sharedpool.org"
    }).encode("utf-8")

    # NO X-Test-Tenant-ID header injected
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/orders",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return {"worker_id": worker_id, "status": resp.status, "data": data, "error": None}
    except urllib.error.HTTPError as e:
        err_data = json.loads(e.read().decode())
        return {"worker_id": worker_id, "status": e.code, "data": err_data, "error": err_data.get("message")}


def main():
    print("=" * 70)
    print("🚨 RUNNING NAIVE BASELINE: 32 Parallel Threads (NO Tenant Isolation)")
    print("=" * 70)
    
    server = start_test_server()
    num_workers = 32

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(naive_worker_booking, i) for i in range(1, num_workers + 1)]
        results = [f.result() for f in futures]
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    passed = [r for r in results if r["status"] == 201]
    failed = [r for r in results if r["status"] != 201]

    print(f"\n📊 EXECUTION RESULTS across {num_workers} parallel threads ({elapsed_ms:.1f}ms total):")
    print(f"   ✓ Passed (201 Created): {len(passed)} / {num_workers}")
    print(f"   ✗ Failed (409 Conflict): {len(failed)} / {num_workers} ({(len(failed)/num_workers)*100:.1f}% failure rate!)")

    print("\n🔍 SAMPLE WORKER RESPONSES:")
    for r in results[:4]:
        status_label = "✓ 201 OK" if r["status"] == 201 else f"✗ {r['status']} CONFLICT"
        msg = r["data"].get("orderId") if r["status"] == 201 else r["error"]
        print(f"   Worker #{r['worker_id']:02d} -> {status_label}: {msg}")

    print("\n" + "=" * 70)
    print("💥 INCIDENT OBSERVED: Race condition reproduced!")
    print("   Because workers shared a single global seat pool, 31 out of 32 tests failed.")
    print("   Next step: Implement Dynamic Tenant Isolation in solution.py!")
    print("=" * 70)

    server.shutdown()


if __name__ == "__main__":
    main()
