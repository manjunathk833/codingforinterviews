#!/usr/bin/env python3
"""Comprehensive CI & Phase 1 Verification Suite for the MAANG Learning Hub (`hub/`) & AeroCart AUT (`apps/aerocart/`).

Tests 10 End-to-End Suites:
1. State Engine (`hub/state_manager.py`): `MASTER_SHEET.md` + `PRACTICE_CYCLE.md` bi-directional sync
2. Concept Feed & Gamification: Quiz scoring (+50 XP), idempotency, and bookmark toggling
3. DSA Step-by-Step Visualizer Traces: Group Anagrams, Two Sum, Valid Anagram (default + custom inputs)
4. Systems Architecture Simulator Traces: Playwright vs Selenium, 32-Worker Isolation, Endpoint-Cloud Sync
5. Live Dual-Language Test Runner Bridge (`hub/server.py` -> Java 17 + Python 3) & Web UI Bundle
6. Learning Hub HTTP API Routing (`GET /`, `/api/health`, `/api/dashboard`, `/api/feed`, `/api/visualizers`, `POST /api/visualize`, `404`)
7. AeroCart AUT Microservice Endpoints: Auth JWT, Flight Search, Token Bucket Rate Limiter (HTTP 429), and RAG Concierge Modes
8. Distributed Concurrency Kata: 32-Thread Shared Collision (1/32 pass, 31/32 HTTP 409) vs Dynamic Tenant Isolation (32/32 pass)
9. Eventual Consistency Saga: Asynchronous Order State Machine (`PENDING` -> `CONFIRMED` after 300ms Kafka lag)
10. CLI Tooling Integrity: `tools/tracker.py summary`, `tools/cycle.py status`, and `tools/cycle.py next`
"""

import concurrent.futures
import subprocess
import sys
import time
import unittest
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hub import state_manager, visualizer_engine, server as hub_server
from apps.aerocart import server as aerocart_server
from apps.aerocart.client import AeroCartClient


class TestHubAndArchitectureCI(unittest.TestCase):
    """End-to-end verification of Phase 1 Learning Hub, AeroCart AUT, and CLI Tooling."""

    def setUp(self):
        # Backup existing db.json if present so tests leave clean state
        self.db_path = state_manager.DB_PATH
        self.db_backup = None
        if self.db_path.exists():
            self.db_backup = self.db_path.read_text(encoding="utf-8")
        elif self.db_path.exists():
            self.db_path.unlink()
        aerocart_server.dispatch_request("POST", "/api/v1/admin/reset")

    def tearDown(self):
        if self.db_backup is not None:
            self.db_path.write_text(self.db_backup, encoding="utf-8")
        elif self.db_path.exists():
            self.db_path.unlink()

    def test_01_dashboard_state_and_markdown_sync(self):
        """Verify bi-directional parser for MASTER_SHEET.md, PRACTICE_CYCLE.md, and runnable problems."""
        payload = state_manager.get_dashboard_payload()

        self.assertIn("dsa", payload)
        dsa = payload["dsa"]
        self.assertEqual(dsa["total"], 128, "Expected 128 total problems in MASTER_SHEET.md")
        self.assertGreaterEqual(dsa["bothDone"], 3, "Expected at least 3 completed DSA problems")
        self.assertGreaterEqual(len(dsa["byPattern"]), 15, "Expected all DSA patterns parsed")

        runnable_folders = {p["folderSlug"] for p in dsa["problems"] if p["hasLocalFiles"]}
        self.assertIn("001-two-sum", runnable_folders)
        self.assertIn("002-valid-anagram", runnable_folders)
        self.assertIn("003-group-anagrams", runnable_folders)

        cycle = payload["practiceCycle"]
        self.assertEqual(len(cycle["stages"]), 4, "Expected 4 stages in Practice Cycle")
        self.assertEqual(cycle["stages"][0]["command"], "./run.sh test 003-group-anagrams")
        self.assertGreaterEqual(payload["readinessScore"], 605)

    def test_02_concept_feed_and_xp_progression(self):
        """Verify Concept Feed cards, quiz completion (+50 XP), idempotency, and bookmark toggle."""
        feed_initial = state_manager.get_feed_payload()
        cards = feed_initial["cards"]
        self.assertGreaterEqual(len(cards), 6, "Expected at least 6 micro-learning concept cards")

        categories = {c["category"] for c in cards}
        for expected_cat in ("DSA Invariants", "OS Internals", "Computer Networks", "System Design", "AI & RAG"):
            self.assertIn(expected_cat, categories)

        target_card = cards[0]
        target_card_id = target_card["id"]
        correct_idx = target_card["quiz"]["correctIndex"]

        res1 = state_manager.record_feed_interaction(target_card_id, "quiz", correct_idx)
        self.assertEqual(res1["status"], "ok")
        self.assertIn(target_card_id, res1["completedCards"])
        xp_after_first = res1["xp"]
        self.assertEqual(xp_after_first, 300)

        res2 = state_manager.record_feed_interaction(target_card_id, "quiz", correct_idx)
        self.assertEqual(res2["xp"], xp_after_first, "Repeat quiz completion must not double-count XP")

        bm_on = state_manager.record_feed_interaction(target_card_id, "toggle_bookmark")
        self.assertIn(target_card_id, bm_on["bookmarkedCards"])
        bm_off = state_manager.record_feed_interaction(target_card_id, "toggle_bookmark")
        self.assertNotIn(target_card_id, bm_off["bookmarkedCards"])

    def test_03_visualizer_catalog_and_dsa_traces(self):
        """Verify step-by-step trace generation for all DSA visualizers with default and custom inputs."""
        catalog = visualizer_engine.list_visualizers()
        ids = {item["id"] for item in catalog}
        expected_ids = {
            "dsa-group-anagrams",
            "dsa-two-sum",
            "dsa-valid-anagram",
            "arch-playwright-vs-selenium",
            "arch-concurrency-isolation",
            "arch-endpoint-cloud-sync",
        }
        self.assertTrue(expected_ids.issubset(ids))

        ga_trace = visualizer_engine.generate_trace(
            "dsa-group-anagrams", {"strs": ["cab", "bca", "xyz"]}
        )
        self.assertEqual(ga_trace["visualizerId"], "dsa-group-anagrams")
        self.assertEqual(len(ga_trace["steps"]), 8)
        self.assertEqual(len(ga_trace["steps"][-1]["buckets"]), 2)

        ts_trace = visualizer_engine.generate_trace(
            "dsa-two-sum", {"nums": [3, 2, 4], "target": 6}
        )
        self.assertEqual(ts_trace["steps"][-1]["matchedIndices"], [1, 2])

        va_trace = visualizer_engine.generate_trace(
            "dsa-valid-anagram", {"s": "rat", "t": "car"}
        )
        self.assertFalse(va_trace["steps"][-1]["isAnagram"])

    def test_04_architecture_simulator_traces(self):
        """Verify step-by-step trace generation for all 3 Systems Architecture visualizers."""
        for arch_id in (
            "arch-playwright-vs-selenium",
            "arch-concurrency-isolation",
            "arch-endpoint-cloud-sync",
        ):
            trace = visualizer_engine.generate_trace(arch_id)
            self.assertEqual(trace["type"], "architecture-compare")
            self.assertGreaterEqual(len(trace["steps"]), 3)
            for step in trace["steps"]:
                self.assertIn("leftTitle", step)
                self.assertIn("rightTitle", step)
                self.assertIn("leftMetrics", step)
                self.assertIn("rightMetrics", step)

    def test_05_live_test_runner_bridge_and_ui_bundle(self):
        """Verify live Java + Python test execution via hub_server.execute_test_target and HTML integrity."""
        test_res = hub_server.execute_test_target("003-group-anagrams", "all")
        self.assertEqual(test_res["status"], "PASSED", f"Expected 003-group-anagrams to pass: {test_res}")
        self.assertEqual(test_res["exitCode"], 0)
        self.assertIn("PASS Java", test_res["output"])
        self.assertIn("PASS Python", test_res["output"])

        # Reject invalid shell-injection target strings safely
        bad_res = hub_server.execute_test_target("001-two-sum; rm -rf /", "all")
        self.assertEqual(bad_res["status"], "ERROR")

        html_path = REPO_ROOT / "hub" / "static" / "index.html"
        self.assertTrue(html_path.exists())
        html = html_path.read_text(encoding="utf-8")
        self.assertIn("tab-btn-feed", html)
        self.assertIn("tab-btn-visualizer", html)
        self.assertIn("tab-btn-dashboard", html)
        self.assertIn("/api/visualize", html)
        self.assertIn("/api/run-test", html)

    def test_06_hub_http_endpoints_and_routing(self):
        """Verify LearningHubHandler HTTP endpoints (GET /, /api/health, /api/dashboard, /api/feed, POST /api/visualize, 404)."""
        root_res = hub_server.dispatch_request("GET", "/")
        self.assertEqual(root_res["status_code"], 200)
        self.assertIn("Antigravity Learning Hub", root_res["data"]["html"])

        health_res = hub_server.dispatch_request("GET", "/api/health")
        self.assertEqual(health_res["status_code"], 200)
        self.assertEqual(health_res["data"]["status"], "UP")

        dash_res = hub_server.dispatch_request("GET", "/api/dashboard")
        self.assertEqual(dash_res["status_code"], 200)
        self.assertEqual(dash_res["data"]["dsa"]["total"], 128)

        viz_list_res = hub_server.dispatch_request("GET", "/api/visualizers")
        self.assertEqual(viz_list_res["status_code"], 200)
        self.assertEqual(len(viz_list_res["data"]["visualizers"]), 6)

        viz_post_res = hub_server.dispatch_request(
            "POST",
            "/api/visualize",
            body={"visualizerId": "dsa-two-sum", "customInput": {"nums": [1, 5, 9], "target": 10}}
        )
        self.assertEqual(viz_post_res["status_code"], 200)
        self.assertEqual(viz_post_res["data"]["steps"][-1]["matchedIndices"], [0, 2])

        not_found_res = hub_server.dispatch_request("GET", "/api/non-existent")
        self.assertEqual(not_found_res["status_code"], 404)

    def test_07_aerocart_aut_microservices_and_rate_limiter(self):
        """Verify AeroCart AUT endpoints: Auth, Flight Search, Token Bucket Rate Limiter (429), and RAG Concierge."""
        client = AeroCartClient(in_process=True)

        login_ok = client.login("sdet@maang.io", "secret123")
        self.assertEqual(login_ok["status_code"], 200)
        self.assertIn("accessToken", login_ok["data"])

        login_bad = client.login("sdet@maang.io", "invalid")
        self.assertEqual(login_bad["status_code"], 401)

        flights = client.search_flights("JFK", "LHR")
        self.assertEqual(flights["status_code"], 200)
        self.assertEqual(flights["data"]["count"], 2)

        # Token Bucket Rate Limiter: 5 requests/sec allowed, 6th returns HTTP 429
        for _ in range(5):
            rl_res = aerocart_server.dispatch_request("GET", "/api/v1/chaos/rate-limit", client_ip="10.0.0.99")
            self.assertEqual(rl_res["status_code"], 200)
        rl_blocked = aerocart_server.dispatch_request("GET", "/api/v1/chaos/rate-limit", client_ip="10.0.0.99")
        self.assertEqual(rl_blocked["status_code"], 429)

        # RAG Concierge modes
        rag_grounded = client.ask_concierge("What is the 24 hour cancellation policy?", mode="grounded")
        self.assertEqual(rag_grounded["status_code"], 200)
        self.assertEqual(rag_grounded["data"]["matchedDocId"], "doc_24h_rule")
        self.assertIn("7 days", rag_grounded["data"]["answer"])

        rag_hallucinated = client.ask_concierge("What is the 24 hour cancellation policy?", mode="hallucinated")
        self.assertIn("no restrictions", rag_hallucinated["data"]["answer"])

    def test_08_aerocart_concurrency_collision_vs_tenant_isolation(self):
        """Verify 32 parallel workers collide in shared mode (1/32 pass) and succeed in isolated mode (32/32 pass)."""
        client = AeroCartClient(in_process=True)
        client.reset_state()

        num_workers = 32
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as pool:
            naive_results = list(pool.map(lambda i: client.create_order("AI-202", "1A", f"w{i}@test.io", tenant_id=None), range(num_workers)))
        naive_201 = sum(1 for r in naive_results if r["status_code"] == 201)
        naive_409 = sum(1 for r in naive_results if r["status_code"] == 409)
        self.assertEqual(naive_201, 1)
        self.assertEqual(naive_409, 31)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as pool:
            iso_results = list(pool.map(
                lambda i: client.create_order("AI-202", "1A", f"w{i}@test.io", tenant_id=f"tenant_{i}_{uuid.uuid4().hex[:6]}"),
                range(num_workers)
            ))
        iso_201 = sum(1 for r in iso_results if r["status_code"] == 201)
        self.assertEqual(iso_201, 32)

    def test_09_aerocart_eventual_consistency_saga(self):
        """Verify asynchronous order saga starts as PENDING and transitions to CONFIRMED after 300ms."""
        client = AeroCartClient(in_process=True)
        order_res = client.create_order("AI-202", "2B", "saga@test.io", tenant_id="tenant_saga_test")
        self.assertEqual(order_res["status_code"], 201)
        order_id = order_res["data"]["orderId"]

        immediate_poll = client.get_order(order_id)
        self.assertEqual(immediate_poll["data"]["status"], "PENDING")

        time.sleep(0.32)
        confirmed_poll = client.get_order(order_id)
        self.assertEqual(confirmed_poll["data"]["status"], "CONFIRMED")

    def test_10_cli_tools_tracker_and_cycle_integrity(self):
        """Verify tools/tracker.py summary and tools/cycle.py status/next execute cleanly."""
        for cmd in (
            [sys.executable, str(REPO_ROOT / "tools" / "tracker.py"), "summary"],
            [sys.executable, str(REPO_ROOT / "tools" / "cycle.py"), "status"],
            [sys.executable, str(REPO_ROOT / "tools" / "cycle.py"), "next"],
        ):
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=10)
            self.assertEqual(proc.returncode, 0, f"Command {cmd} failed: {proc.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
