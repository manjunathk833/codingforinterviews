#!/usr/bin/env python3
"""
Antigravity Learning Hub — Unified Local Server & Visualization Engine.
Runs on http://127.0.0.1:8090 (or custom port via HUB_PORT / CLI argument).
Zero external dependencies required.
"""

import json
import os
import re
import subprocess
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hub import state_manager, visualizer_engine

DEFAULT_PORT = int(os.environ.get("HUB_PORT", 8090))
STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"


def execute_test_target(target: str, lang: str = "all") -> dict:
    """Safely execute `./run.sh test <target> --lang <lang>` and return output."""
    if not target or not re.match(r"^[a-zA-Z0-9_\-/]+$", target):
        return {"status": "ERROR", "exitCode": 1, "output": "Invalid target slug.", "durationMs": 0}
    if lang not in ("all", "java", "python"):
        lang = "all"

    cmd = ["python3", str(REPO_ROOT / "tools" / "runner.py"), "test", target, "--lang", lang]
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=25
        )
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        raw_out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        # Strip ANSI escape codes for clean web rendering
        clean_out = re.sub(r"\x1b\[[0-9;]*m", "", raw_out).strip()
        return {
            "status": "PASSED" if proc.returncode == 0 else "FAILED",
            "exitCode": proc.returncode,
            "target": target,
            "lang": lang,
            "durationMs": elapsed_ms,
            "output": clean_out
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "exitCode": 124,
            "target": target,
            "lang": lang,
            "durationMs": 25000,
            "output": "Execution timed out after 25s."
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "exitCode": 1,
            "target": target,
            "lang": lang,
            "durationMs": 0,
            "output": str(e)
        }


class LearningHubHandler(BaseHTTPRequestHandler):

    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            if STATIC_INDEX.exists():
                html_bytes = STATIC_INDEX.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
            else:
                self._send_json(404, {"error": "Static UI index.html not found"})
            return

        if path == "/api/health":
            self._send_json(200, {"status": "UP", "service": "antigravity-learning-hub"})
            return

        if path == "/api/dashboard":
            self._send_json(200, state_manager.get_dashboard_payload())
            return

        if path == "/api/feed":
            self._send_json(200, state_manager.get_feed_payload())
            return

        if path == "/api/visualizers":
            self._send_json(200, {"visualizers": visualizer_engine.list_visualizers()})
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception:
            payload = {}

        if path == "/api/feed/interact":
            card_id = payload.get("cardId", "")
            action = payload.get("action", "complete")
            selected_option = payload.get("selectedOption")
            res = state_manager.record_feed_interaction(card_id, action, selected_option)
            self._send_json(200, res)
            return

        if path == "/api/visualize":
            viz_id = payload.get("visualizerId", "dsa-group-anagrams")
            custom_input = payload.get("customInput")
            trace = visualizer_engine.generate_trace(viz_id, custom_input)
            self._send_json(200, trace)
            return

        if path == "/api/run-test":
            target = payload.get("target", "001-two-sum")
            lang = payload.get("lang", "all")
            res = execute_test_target(target, lang)
            self._send_json(200, res)
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def log_message(self, format, *args):
        if "DEBUG_HUB" in os.environ:
            super().log_message(format, *args)


class ThreadedHubServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128


def dispatch_request(method: str, path: str, body: dict = None, headers: dict = None) -> dict:
    """In-process HTTP request dispatcher for LearningHubHandler (for fast unit & CI tests)."""
    import io

    raw_body = json.dumps(body).encode("utf-8") if body is not None else b""
    req_headers = {"Content-Length": str(len(raw_body)), "Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    handler = LearningHubHandler.__new__(LearningHubHandler)
    handler.path = path
    handler.command = method.upper()
    handler.headers = req_headers
    handler.client_address = ("127.0.0.1", 0)
    handler.rfile = io.BytesIO(raw_body)
    handler.wfile = io.BytesIO()
    handler._resp_status = 200
    handler._resp_headers = {}

    def _send_response(code, message=None):
        handler._resp_status = code

    def _send_header(k, v):
        handler._resp_headers[k] = v

    def _end_headers():
        pass

    handler.send_response = _send_response
    handler.send_header = _send_header
    handler.end_headers = _end_headers

    if handler.command == "GET":
        handler.do_GET()
    elif handler.command == "POST":
        handler.do_POST()
    elif handler.command == "OPTIONS":
        handler.do_OPTIONS()

    out_bytes = handler.wfile.getvalue()
    out_text = out_bytes.decode("utf-8", errors="replace")
    try:
        parsed_data = json.loads(out_text) if out_text and not out_text.lstrip().startswith("<!DOCTYPE") else {"html": out_text}
    except Exception:
        parsed_data = {"raw": out_text}

    return {
        "status_code": handler._resp_status,
        "data": parsed_data,
        "headers": handler._resp_headers
    }


def run_hub_server(port: int = DEFAULT_PORT, host: str = "127.0.0.1"):
    server = ThreadedHubServer((host, port), LearningHubHandler)
    print("=" * 68)
    print(f"🚀 ANTIGRAVITY LEARNING HUB & VISUALIZER RUNNING")
    print(f"🌐 Open in Browser: http://{host}:{port}")
    print("=" * 68)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Antigravity Learning Hub...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Learning Hub Server")
    parser.add_argument("pos_port", nargs="?", type=int, default=None, help="Optional positional port")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port (default: 8090)")
    args = parser.parse_args()
    final_port = args.pos_port if args.pos_port is not None else args.port
    run_hub_server(final_port, args.host)
