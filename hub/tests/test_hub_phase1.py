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
        # Backup existing db.json if present and start each test with a fresh default DB
        self.db_path = state_manager.DB_PATH
        self.db_backup = None
        if self.db_path.exists():
            self.db_backup = self.db_path.read_text(encoding="utf-8")
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
        self.assertGreaterEqual(len(cards), 10, "Expected at least 10 micro-learning concept cards (Phase 1 + Phase 2)")

        categories = {c["category"] for c in cards}
        for expected_cat in (
            "DSA Invariants",
            "OS Internals",
            "Computer Networks",
            "Database Internals",
            "System Design",
            "AI & RAG",
        ):
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
            "cs-os-leak-detector",
            "cs-tcp-tls-handshake",
            "ai-rag-triad-gate",
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
        """Verify step-by-step trace generation for all 6 Systems Architecture, Core CS & AI visualizers."""
        for arch_id in (
            "arch-playwright-vs-selenium",
            "arch-concurrency-isolation",
            "arch-endpoint-cloud-sync",
            "cs-os-leak-detector",
            "cs-tcp-tls-handshake",
            "ai-rag-triad-gate",
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

        proto_res = hub_server.dispatch_request("GET", "/prototype")
        self.assertEqual(proto_res["status_code"], 200)
        self.assertIn("Zen Editorial Studio", proto_res["data"]["html"])

        health_res = hub_server.dispatch_request("GET", "/api/health")
        self.assertEqual(health_res["status_code"], 200)
        self.assertEqual(health_res["data"]["status"], "UP")

        dash_res = hub_server.dispatch_request("GET", "/api/dashboard")
        self.assertEqual(dash_res["status_code"], 200)
        self.assertEqual(dash_res["data"]["dsa"]["total"], 128)

        viz_list_res = hub_server.dispatch_request("GET", "/api/visualizers")
        self.assertEqual(viz_list_res["status_code"], 200)
        self.assertEqual(len(viz_list_res["data"]["visualizers"]), 9)

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

    def test_11_phase2_core_cs_system_design_and_ai_labs(self):
        """Verify all 6 Curriculum Pillars and all 7 Phase 2 dual-language labs (Java 17 & Python 3)."""
        dash = state_manager.get_dashboard_payload()
        pillar_ids = {p["id"] for p in dash["pillars"]}
        self.assertEqual(
            pillar_ids,
            {"dsa", "core-cs", "system-design", "ai-engineering", "frameworks", "mock-interviews"}
        )

        lab_slugs = {l["folderSlug"] for l in dash["architectureLabs"]}
        phase2_slugs = [
            "01-memory-and-handle-leak-detector",
            "01-tcp-tls-and-proxy-inspector",
            "01-wal-and-isolation-anomalies",
            "01-endpoint-to-cloud-sync-and-jitter",
            "02-consistent-hashing-and-grid-sharding",
            "01-rag-triad-evaluator",
            "02-self-healing-locators-and-ast",
        ]
        for slug in phase2_slugs:
            self.assertIn(slug, lab_slugs, f"Missing Phase 2 lab {slug} in dashboard architectureLabs")
            res = hub_server.execute_test_target(slug, "all")
            self.assertEqual(res["status"], "PASSED", f"Phase 2 lab {slug} failed: {res}")
            self.assertIn("PASS Java", res["output"])
            self.assertIn("PASS Python", res["output"])

    def test_12_phase3_telegram_bot_router_and_callbacks(self):
        """Verify Phase 3 Telegram Bot command router, natural language program lookup, and inline quiz callbacks."""
        from hub import telegram_bot

        bot = telegram_bot.AntigravityTelegramBot(token="dummy_token", chat_id="12345")
        # Mock _api_call so unit tests never make external network calls in CI
        bot._api_call = lambda method, payload=None, timeout=15: {"ok": True, "result": {}}

        # 1. /start menu
        start_reply = bot.handle_command_text("/start")
        self.assertIn("ANTIGRAVITY MOBILE LEARNING HUB", start_reply["text"])
        self.assertIn("inline_keyboard", start_reply["reply_markup"])

        # 2. Natural-language program request: "give me a program on group anagrams"
        prog_reply = bot.handle_command_text("give me a program on group anagrams")
        self.assertIn("003-group-anagrams", prog_reply["text"])
        self.assertIn("class Solution", prog_reply["text"])

        # 3. Switch program language callback to Java
        java_cb = bot.handle_callback_query("cb_1", "prog_lang:003-group-anagrams:java")
        self.assertIn("public class Solution", java_cb["text"])

        # 4. Concept card & inline quiz callback (+50 XP sync)
        card = state_manager.CONCEPT_FEED_CARDS[0]
        correct_idx = card["quiz"]["correctIndex"]
        quiz_cb = bot.handle_callback_query("cb_2", f"quiz_ans:{card['id']}:{correct_idx}")
        self.assertIn("CORRECT", quiz_cb["text"])

        # 5. Remote test execution via Telegram "/test 01-memory-and-handle-leak-detector"
        test_reply = bot.handle_command_text("/test 01-memory-and-handle-leak-detector")
        self.assertIn("PASSED", test_reply["text"])

        # 6. Verify /api/telegram/status endpoint on Hub server
        tg_status = hub_server.dispatch_request("GET", "/api/telegram/status")
        self.assertEqual(tg_status["status_code"], 200)
        self.assertIn("configured", tg_status["data"])

    def test_13_localhost_cors_and_dns_rebinding_protection(self):
        """Verify wildcard CORS is removed and cross-origin CSRF / DNS rebinding requests are rejected with 403."""
        # 1. Standard same-origin request without Origin header succeeds and has no wildcard CORS header
        res_ok = hub_server.dispatch_request("GET", "/api/health", headers={"Host": "127.0.0.1:8090"})
        self.assertEqual(res_ok["status_code"], 200)
        self.assertNotEqual(res_ok["headers"].get("Access-Control-Allow-Origin"), "*")

        # 2. Localhost Vite/Hub Origin is allowed and echoed back
        res_local_origin = hub_server.dispatch_request(
            "POST",
            "/api/visualize",
            body={"visualizerId": "dsa-two-sum"},
            headers={"Host": "127.0.0.1:8090", "Origin": "http://127.0.0.1:5173"}
        )
        self.assertEqual(res_local_origin["status_code"], 200)
        self.assertEqual(res_local_origin["headers"].get("Access-Control-Allow-Origin"), "http://127.0.0.1:5173")

        # 3. Cross-origin POST to /api/run-test is blocked with 403 Forbidden
        res_csrf = hub_server.dispatch_request(
            "POST",
            "/api/run-test",
            body={"target": "001-two-sum"},
            headers={"Host": "127.0.0.1:8090", "Origin": "https://evil.example.com"}
        )
        self.assertEqual(res_csrf["status_code"], 403)
        self.assertNotIn("Access-Control-Allow-Origin", res_csrf["headers"])

        # 4. Null origin (sandboxed iframe CSRF) is blocked with 403 Forbidden
        res_null_origin = hub_server.dispatch_request(
            "POST",
            "/api/run-test",
            body={"target": "001-two-sum"},
            headers={"Host": "127.0.0.1:8090", "Origin": "null"}
        )
        self.assertEqual(res_null_origin["status_code"], 403)

        # 5. DNS rebinding attack with external Host header is blocked with 403 Forbidden
        res_rebind = hub_server.dispatch_request(
            "GET",
            "/api/dashboard",
            headers={"Host": "rebind-attacker.com:8090"}
        )
        self.assertEqual(res_rebind["status_code"], 403)

    def test_14_phase4_filesystem_sync_optimistic_locking_and_per_case_runner(self):
        """Verify Phase 4 bidirectional filesystem sync, sha256 optimistic locking (412), path jail, and tests.json runner."""
        rel_py = "dsa/01-arrays-and-hashing/003-group-anagrams/solution.py"

        # 1. Problem bundle endpoint returns tests.json metadata + live disk files
        prob_res = hub_server.dispatch_request("GET", "/api/dsa/problem?slug=003-group-anagrams")
        self.assertEqual(prob_res["status_code"], 200)
        self.assertEqual(prob_res["data"]["problem"]["slug"], "003-group-anagrams")
        self.assertEqual(len(prob_res["data"]["problem"]["cases"]), 3)
        self.assertEqual(len(prob_res["data"]["problem"]["hints"]), 4)
        self.assertIn("python", prob_res["data"]["files"])
        self.assertIn("java", prob_res["data"]["files"])

        # 2. Read file via GET /api/fs/file
        read_res = hub_server.dispatch_request("GET", f"/api/fs/file?path={rel_py}")
        self.assertEqual(read_res["status_code"], 200)
        orig_content = read_res["data"]["content"]
        orig_sha = read_res["data"]["sha256"]
        self.assertIn("def groupAnagrams", orig_content)

        # 3. Path traversal jail blocks access outside allowed curriculum folders
        for blocked_path in ("../../etc/passwd", ".env", "hub/server.py"):
            bad_res = hub_server.dispatch_request("GET", f"/api/fs/file?path={blocked_path}")
            self.assertEqual(bad_res["status_code"], 403)

        # 4. Stale If-Match / expectedSha256 triggers HTTP 412 Precondition Failed
        conflict_res = hub_server.dispatch_request(
            "PUT",
            "/api/fs/file",
            body={"path": rel_py, "content": orig_content, "expectedSha256": "deadbeef0000"}
        )
        self.assertEqual(conflict_res["status_code"], 412)
        self.assertEqual(conflict_res["data"]["diskSha256"], orig_sha)

        # 5. Valid atomic write with matching sha256 succeeds and preserves content
        write_res = hub_server.dispatch_request(
            "PUT",
            "/api/fs/file",
            body={"path": rel_py, "content": orig_content, "expectedSha256": orig_sha}
        )
        self.assertEqual(write_res["status_code"], 200)
        self.assertEqual(write_res["data"]["sha256"], orig_sha)

        # 6. Per-case runner (POST /api/run-cases) executes tests.json for 001, 002, and 003
        for slug, expected_count in (
            ("001-two-sum", 4),
            ("002-valid-anagram", 4),
            ("003-group-anagrams", 3),
        ):
            cases_res = hub_server.dispatch_request(
                "POST",
                "/api/run-cases",
                body={"slug": slug, "lang": "python"}
            )
            self.assertEqual(cases_res["status_code"], 200)
            self.assertEqual(cases_res["data"]["status"], "PASSED", f"Failed cases for {slug}: {cases_res['data']}")
            self.assertEqual(len(cases_res["data"]["cases"]), expected_count)
            self.assertTrue(all(c["passed"] for c in cases_res["data"]["cases"]))

    def test_15_milestones_1_to_4_dynamic_chapters_scaffolder_and_stat(self):
        """Verify 15 dynamic DSA chapters, live IDE stat endpoint, and 1-click problem scaffolder."""
        import shutil

        # 1. Verify all 15 chapters and recommendedProblem in /api/dashboard
        dash_res = hub_server.dispatch_request("GET", "/api/dashboard")
        self.assertEqual(dash_res["status_code"], 200)
        dsa = dash_res["data"]["dsa"]
        self.assertEqual(len(dsa["chapters"]), 15)
        self.assertEqual(dsa["chapters"][0]["title"], "Ch 01: Arrays & Hashing")
        self.assertIsNotNone(dsa["recommendedProblem"])

        # 2. Verify GET /api/fs/stat returns sha256 & mtimeMs for live IDE file watching
        rel_py = "dsa/01-arrays-and-hashing/003-group-anagrams/solution.py"
        stat_res = hub_server.dispatch_request("GET", f"/api/fs/stat?path={rel_py}")
        self.assertEqual(stat_res["status_code"], 200)
        self.assertIn("sha256", stat_res["data"])
        self.assertIn("mtimeMs", stat_res["data"])

        # 3. Verify POST /api/dsa/scaffold creates a missing problem folder and cleans up after test
        scaf_dir = REPO_ROOT / "dsa" / "01-arrays-and-hashing" / "002-contains-duplicate"
        existed_before = scaf_dir.exists()
        try:
            scaf_res = hub_server.dispatch_request(
                "POST",
                "/api/dsa/scaffold",
                body={"problemId": 2, "slug": "contains-duplicate"}
            )
            self.assertEqual(scaf_res["status_code"], 200)
            self.assertTrue((scaf_dir / "solution.py").exists())
            self.assertTrue((scaf_dir / "Solution.java").exists())
            self.assertTrue((scaf_dir / "tests.json").exists())
            # Verify scaffolded starter passes per-case runner
            run_scaf = hub_server.dispatch_request(
                "POST",
                "/api/run-cases",
                body={"slug": "002-contains-duplicate", "lang": "python"}
            )
            self.assertEqual(run_scaf["status_code"], 200)
            self.assertEqual(run_scaf["data"]["status"], "PASSED")
        finally:
            if not existed_before and scaf_dir.exists():
                shutil.rmtree(scaf_dir)

    def test_16_phase2_sqlite_fts5_knowledgebase_newsfeed_and_workbench(self):
        """Verify Phase 2 SQLite WAL + FTS5 Knowledgebase, Newsfeed cross-linking, Quiz grading, Local Workbench, and Mock Interviews."""
        from hub import storage

        # 1. GET /api/tracks returns all 6 tracks across the 4 execution archetypes
        tracks_res = hub_server.dispatch_request("GET", "/api/tracks")
        self.assertEqual(tracks_res["status_code"], 200)
        tracks = tracks_res["data"]["tracks"]
        self.assertEqual(len(tracks), 6)
        archetypes = {t["archetype"] for t in tracks}
        self.assertEqual(
            archetypes,
            {"interactive-textbook", "in-browser-studio", "local-ide-workbench", "mock-interview-simulator"},
        )

        # 2. GET /api/kb/chapters & GET /api/kb/chapter return structured textbook chapters with quizzes & relatedNews
        ch_list_res = hub_server.dispatch_request("GET", "/api/kb/chapters")
        self.assertEqual(ch_list_res["status_code"], 200)
        chapters = ch_list_res["data"]["chapters"]
        self.assertGreaterEqual(len(chapters), 8)

        ch_detail = hub_server.dispatch_request("GET", "/api/kb/chapter?slug=cs-03-lsm-trees-b-trees-and-wal-isolation")
        self.assertEqual(ch_detail["status_code"], 200)
        self.assertEqual(ch_detail["data"]["track"], "core-cs")
        self.assertGreaterEqual(len(ch_detail["data"]["quizzes"]), 3)
        self.assertGreaterEqual(len(ch_detail["data"]["relatedNews"]), 1)

        # 3. GET /api/kb/search executes FTS5 BM25 queries including hyphenated/slash technical terms
        for query_term, expected_slug_prefix in (
            ("LSM-Tree", "cs-03-lsm-trees"),
            ("HTTP/2", "cs-02-tcp-tls"),
            ("Consistent Hashing", "sd-02-consistent-hashing"),
            ("Token Bucket", "sd-01-continuous-sync"),
            ("RAG Entailment", "ai-01-rag-triad"),
        ):
            from urllib.parse import quote
            s_res = hub_server.dispatch_request("GET", f"/api/kb/search?q={quote(query_term)}")
            self.assertEqual(s_res["status_code"], 200)
            self.assertGreater(s_res["data"]["count"], 0, f"Expected FTS5 hits for '{query_term}'")
            matched_slugs = [r["slug"] for r in s_res["data"]["results"]]
            self.assertTrue(
                any(slug.startswith(expected_slug_prefix) for slug in matched_slugs),
                f"Expected '{expected_slug_prefix}' in {matched_slugs} for query '{query_term}'",
            )

        # 4. POST /api/kb/quiz grades end-of-chapter quizzes deterministically (and cleans up test attempt)
        quiz_res = hub_server.dispatch_request(
            "POST",
            "/api/kb/quiz",
            body={
                "slug": "sd-01-continuous-sync-and-backpressure",
                "answers": {"sd-01-q1": 1, "sd-01-q2": 1, "sd-01-q3": 2},
            },
        )
        self.assertEqual(quiz_res["status_code"], 200)
        self.assertEqual(quiz_res["data"]["score"], 3)
        self.assertTrue(quiz_res["data"]["mastered"])

        # Clean up test quiz attempt so production DB stays clean
        conn = storage._get_connection()
        conn.execute("DELETE FROM kb_quiz_attempts WHERE slug = 'sd-01-continuous-sync-and-backpressure'")
        conn.commit()
        conn.close()

        # 5. GET /api/newsfeed & POST /api/newsfeed/bookmark
        news_res = hub_server.dispatch_request("GET", "/api/newsfeed?category=ai-engineering")
        self.assertEqual(news_res["status_code"], 200)
        self.assertGreaterEqual(news_res["data"]["count"], 2)
        first_art_id = news_res["data"]["articles"][0]["id"]
        bm_on = hub_server.dispatch_request("POST", "/api/newsfeed/bookmark", body={"articleId": first_art_id})
        self.assertEqual(bm_on["status_code"], 200)
        self.assertTrue(bm_on["data"]["bookmarked"])
        bm_off = hub_server.dispatch_request("POST", "/api/newsfeed/bookmark", body={"articleId": first_art_id})
        self.assertEqual(bm_off["status_code"], 200)
        self.assertFalse(bm_off["data"]["bookmarked"])

        # 6. GET /api/workbench/catalog & POST /api/workbench/verify (100% local deterministic, zero AI)
        wb_res = hub_server.dispatch_request("GET", "/api/workbench/catalog")
        self.assertEqual(wb_res["status_code"], 200)
        self.assertGreaterEqual(len(wb_res["data"]["items"]), 8)
        verify_res = hub_server.dispatch_request(
            "POST",
            "/api/workbench/verify",
            body={"itemId": "wb-rate-limiter-backpressure"},
        )
        self.assertEqual(verify_res["status_code"], 200)
        self.assertEqual(verify_res["data"]["status"], "PASS")

        # 7. GET /api/interviews & GET /api/interviews/session
        mi_res = hub_server.dispatch_request("GET", "/api/interviews")
        self.assertEqual(mi_res["status_code"], 200)
        self.assertGreaterEqual(len(mi_res["data"]["sessions"]), 1)
        mi_sess = hub_server.dispatch_request("GET", "/api/interviews/session?id=interview-1")
        self.assertEqual(mi_sess["status_code"], 200)
        self.assertIn("Question 1", mi_sess["data"]["questionsMarkdown"])

    def test_17_phase3_hub_of_learning_ui_views_and_archetypes(self):
        """Verify Phase 3 Hub of Learning Zen Editorial Studio UI views, FTS5 search bar, Textbook Reader, Newsfeed, and Local Workbench."""
        root_res = hub_server.dispatch_request("GET", "/")
        self.assertEqual(root_res["status_code"], 200)
        html = root_res["data"]["html"]
        for required_token in (
            "The Hub of Learning",
            "tab-btn-textbook",
            "tab-btn-workbench",
            "global-kb-search",
            "view-textbook",
            "view-newsfeed",
            "view-workbench",
            "/api/kb/search",
            "/api/kb/quiz",
            "/api/newsfeed",
            "/api/workbench/verify",
            "/api/interviews/save",
        ):
            self.assertIn(required_token, html, f"Missing UI token '{required_token}' in hub/static/index.html")


if __name__ == "__main__":
    unittest.main(verbosity=2)
