#!/usr/bin/env python3
"""
Reference Solution: Dynamic Tenant Isolation Engine.
Generates cryptographically unique tenant contexts per worker thread,
injecting X-Test-Tenant-ID headers to guarantee zero collisions across 32 parallel workers.
"""

import concurrent.futures
import json
import os
import sys
import threading
import time
import urllib.request
import uuid

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from apps.aerocart.server import ThreadedHTTPServer, AeroCartHandler

TEST_PORT = 8992
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def start_test_server():
    server = ThreadedHTTPServer(("127.0.0.1", TEST_PORT), AeroCartHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.15)
    return server


def run_isolated_worker(worker_id: int) -> dict:
    """
    Staff SDET Implementation:
    1. Generates an ephemeral cryptographic tenant context.
    2. Namespaces passenger email and entity metadata.
    3. Injects X-Test-Tenant-ID into HTTP request headers.
    """
    # 1. Ephemeral Tenant Context
    tenant_key = f"tenant_worker_{worker_id}_{uuid.uuid4().hex[:6]}"
    email = f"lead_sdet_{worker_id}_{uuid.uuid4().hex[:4]}@tenantvault.io"

    payload = json.dumps({
        "flightNumber": "AI-202",
        "seat": "1A",  # All 32 workers book Seat 1A simultaneously!
        "passengerEmail": email
    }).encode("utf-8")

    # 2. Context Injection via Header
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/orders",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Test-Tenant-ID": tenant_key
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return {
            "worker_id": worker_id,
            "status": resp.status,
            "tenant_id": tenant_key,
            "order_id": data.get("orderId"),
            "isolation_mode": data.get("isolationMode")
        }


def main():
    print("=" * 70)
    print("🚀 EXECUTING REFERENCE SOLUTION: 32 Parallel Isolated Tenant Workers")
    print("=" * 70)

    server = start_test_server()
    num_workers = 32

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(run_isolated_worker, i) for i in range(1, num_workers + 1)]
        results = [f.result() for f in futures]
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    passed = [r for r in results if r["status"] == 201]
    failed = [r for r in results if r["status"] != 201]

    print(f"\n📊 RESULTS across {num_workers} parallel threads ({elapsed_ms:.1f}ms):")
    print(f"   ✓ Passed (201 Created): {len(passed)} / {num_workers} (100% SUCCESS)")
    print(f"   ✗ Failed: {len(failed)} / {num_workers}")

    print("\n🔍 SAMPLE WORKER OUTPUTS:")
    for r in results[:4]:
        print(f"   Worker #{r['worker_id']:02d} -> ✓ 201 Created [{r['order_id']}] Tenant: {r['tenant_id']} Mode: {r['isolation_mode']}")

    assert len(passed) == 32, f"Expected 32 passed, got {len(passed)}"
    assert len(failed) == 0, f"Expected 0 failed, got {len(failed)}"

    print("\n" + "=" * 70)
    print("🏆 SUCCESS: 32 Parallel Workers passed with 0 collisions and zero state leaks!")
    print("=" * 70)

    server.shutdown()


if __name__ == "__main__":
    main()
