#!/usr/bin/env python3
"""
AeroCart — High-Throughput Airline Booking & Merchant Benchmark Microservice Platform.
Zero-dependency, standalone server designed as the unified Application Under Test (AUT)
for all SDET Automation Frameworks, Concurrency Drills, and AI Evaluations.

Runs natively on macOS (Apple Silicon), Linux, and CI in < 100ms.
"""

import json
import os
import sys
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import threading

PORT = int(os.environ.get("AEROCART_PORT", 8000))

# ------------------------------------------------------------------------------
# In-Memory Distributed State Store (Thread-Safe)
# ------------------------------------------------------------------------------
STATE_LOCK = threading.Lock()

# Global Shared Inventory (for naive concurrency failure simulation)
GLOBAL_INVENTORY = {
    "AI-202": {"totalSeats": 10, "bookedSeats": set(), "flightName": "New York -> London"}
}

# Tenant Partitioned Inventories: tenant_id -> { flight_id: { ... } }
TENANT_INVENTORIES = {}

# Orders: order_id -> { ... }
ORDERS = {}

# Rate Limiter Tracker: ip -> list of timestamps
RATE_LIMIT_BUCKET = {}

# Policy Knowledge Base Chunks (for RAG Evaluation)
POLICY_CHUNKS = [
    {
        "id": "doc_24h_rule",
        "title": "US DOT 24-Hour Cancellation Rule",
        "content": "Passengers may cancel their reservation within 24 hours of booking for a 100% full refund with no cancellation fee, provided the ticket was purchased at least 7 days prior to scheduled flight departure."
    },
    {
        "id": "doc_baggage",
        "title": "International Transatlantic Baggage Policy",
        "content": "Economy class passengers receive one complimentary checked bag (up to 23kg / 50lbs). A second checked bag incurs an $85 USD fee each way. Overweight bags between 23kg and 32kg incur a $100 USD surcharge."
    },
    {
        "id": "doc_eu261",
        "title": "EU Regulation 261/2004 Flight Delay Compensation",
        "content": "For flights departing an EU airport delayed by 3+ hours upon arrival at final destination, passengers are entitled to fixed statutory compensation: €250 for short-haul (<1,500km), €400 for medium-haul, and €600 for long-haul (>3,500km), unless caused by extraordinary circumstances."
    }
]

# ------------------------------------------------------------------------------
# Embedded Single-Page Application (HTML/CSS/JS)
# ------------------------------------------------------------------------------
UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AeroCart — Airline Booking & Concierge</title>
  <style>
    :root { --primary: #0284c7; --primary-dark: #0369a1; --bg: #f8fafc; --card: #ffffff; --text: #0f172a; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 2rem; }
    .container { max-width: 1000px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    h1 { font-size: 1.8rem; color: var(--primary-dark); }
    .badge { background: #e0f2fe; color: #0369a1; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .card { background: var(--card); border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .card h2 { font-size: 1.25rem; margin-bottom: 1rem; }
    input, select, button { width: 100%; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #cbd5e1; margin-bottom: 1rem; font-size: 0.95rem; }
    button { background: var(--primary); color: white; border: none; font-weight: 600; cursor: pointer; transition: background 0.2s; }
    button:hover { background: var(--primary-dark); }
    .seat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1rem; }
    .seat-btn { padding: 0.5rem; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 0.375rem; text-align: center; cursor: pointer; }
    .seat-btn.selected { background: #0284c7; color: white; border-color: #0369a1; }
    .seat-btn.booked { background: #fee2e2; color: #991b1b; cursor: not-allowed; border-color: #fca5a5; }
    .status-box { padding: 1rem; border-radius: 0.5rem; background: #f8fafc; border: 1px solid #e2e8f0; font-family: monospace; font-size: 0.9rem; min-height: 80px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>✈️ AeroCart Platform</h1>
        <p style="color: #64748b; font-size: 0.9rem;">High-Throughput Airline Booking & QE Automation Benchmark</p>
      </div>
      <div>
        <span class="badge" id="system-status">System: Online</span>
      </div>
    </header>

    <div class="grid">
      <!-- Flight Search & Seat Selection -->
      <div class="card">
        <h2>1. Flight Booking Flow</h2>
        <label for="flight-select">Select Flight:</label>
        <select id="flight-select">
          <option value="AI-202">AI-202 (New York JFK → London LHR) - $450</option>
        </select>

        <label>Select Seat:</label>
        <div class="seat-grid" id="seat-map">
          <div class="seat-btn" data-seat="1A">1A</div>
          <div class="seat-btn" data-seat="1B">1B</div>
          <div class="seat-btn" data-seat="2A">2A</div>
          <div class="seat-btn" data-seat="2B">2B</div>
          <div class="seat-btn" data-seat="3A">3A</div>
          <div class="seat-btn" data-seat="3B">3B</div>
        </div>

        <input type="email" id="passenger-email" placeholder="passenger@testvault.org" value="test_traveler@maang.io" />
        <button id="book-flight-btn">Confirm Booking</button>
      </div>

      <!-- Booking Result & Status Monitor -->
      <div class="card">
        <h2>2. Live Saga Order Status</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.75rem;">Simulates asynchronous Kafka event processing & CDC state transitions.</p>
        <div class="status-box" id="order-status-output">Awaiting booking request...</div>
      </div>
    </div>
  </div>

  <script>
    let selectedSeat = "1A";
    const seatButtons = document.querySelectorAll(".seat-btn");
    seatButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        if (btn.classList.contains("booked")) return;
        seatButtons.forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
        selectedSeat = btn.dataset.seat;
      });
    });
    // Set initial selected
    if (seatButtons.length > 0) seatButtons[0].classList.add("selected");

    const bookBtn = document.getElementById("book-flight-btn");
    const statusOutput = document.getElementById("order-status-output");

    bookBtn.addEventListener("click", async () => {
      const email = document.getElementById("passenger-email").value;
      const flight = document.getElementById("flight-select").value;
      statusOutput.innerText = "Initiating booking saga (POST /api/v1/orders)...";

      try {
        const res = await fetch("/api/v1/orders", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ flightNumber: flight, seat: selectedSeat, passengerEmail: email })
        });
        const data = await res.json();
        statusOutput.innerText = "Order Created (HTTP " + res.status + "):\n" + JSON.stringify(data, null, 2);

        if (res.status === 201) {
          // Poll for async confirmation
          statusOutput.innerText += "\\n\\nPolling for asynchronous Kafka confirmation...";
          setTimeout(async () => {
            const pollRes = await fetch("/api/v1/orders/" + data.orderId);
            const pollData = await pollRes.json();
            statusOutput.innerText += "\\n\\n[Kafka Event Processed]:\\n" + JSON.stringify(pollData, null, 2);
          }, 400);
        }
      } catch (err) {
        statusOutput.innerText = "Network Error: " + err.message;
      }
    });
  </script>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# Request Handler
# ------------------------------------------------------------------------------
class AeroCartHandler(BaseHTTPRequestHandler):

    def _send_json(self, status_code: int, data: dict, headers: dict = None):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. UI Root
        if path == "/" or path == "/index.html":
            body = UI_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 2. Health Endpoint
        if path == "/health":
            self._send_json(200, {"status": "UP", "service": "aerocart-monolith"})
            return

        # 3. Flight Search API
        if path == "/api/v1/flights/search":
            flights = [
                {
                    "flightNumber": "AI-202",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departureTime": "2026-11-15T18:30:00Z",
                    "price": 450.00,
                    "availableSeats": 10
                },
                {
                    "flightNumber": "BA-178",
                    "origin": "JFK",
                    "destination": "LHR",
                    "departureTime": "2026-11-15T21:00:00Z",
                    "price": 520.00,
                    "availableSeats": 8
                }
            ]
            self._send_json(200, {"flights": flights, "count": len(flights)})
            return

        # 4. Order Status (with Asynchronous State Machine)
        if path.startswith("/api/v1/orders/"):
            order_id = path.split("/")[-1]
            with STATE_LOCK:
                order = ORDERS.get(order_id)
            if not order:
                self._send_json(404, {"error": "OrderNotFound", "message": f"Order {order_id} not found"})
                return

            # Simulate Kafka consumer event lag: Transitions to CONFIRMED after 300ms
            elapsed_ms = (time.time() - order["createdAt"]) * 1000
            current_status = "CONFIRMED" if elapsed_ms >= 300 else "PENDING"
            
            with STATE_LOCK:
                order["status"] = current_status
            
            self._send_json(200, order)
            return

        # 5. Chaos Endpoint: Latency Simulation (for 504 Triage)
        if path == "/api/v1/chaos/latency":
            qs = parse_qs(parsed.query)
            delay_ms = int(qs.get("ms", [5000])[0])
            time.sleep(delay_ms / 1000.0)
            self._send_json(504, {
                "error": "GatewayTimeout",
                "message": f"Downstream payment gateway failed to respond within {delay_ms}ms SLA.",
                "upstream": "stripe-sandbox-v3",
                "traceId": self.headers.get("X-Test-Trace-ID", "trace_unknown")
            })
            return

        # 6. Chaos Endpoint: Rate Limiter (Token Bucket)
        if path == "/api/v1/chaos/rate-limit":
            client_ip = self.client_address[0]
            now = time.time()
            with STATE_LOCK:
                timestamps = RATE_LIMIT_BUCKET.setdefault(client_ip, [])
                # Keep requests within last 1 second
                timestamps = [t for t in timestamps if now - t < 1.0]
                if len(timestamps) >= 5:
                    RATE_LIMIT_BUCKET[client_ip] = timestamps
                    self._send_json(429, {"error": "TooManyRequests", "retryAfterSeconds": 1})
                    return
                timestamps.append(now)
                RATE_LIMIT_BUCKET[client_ip] = timestamps
            self._send_json(200, {"status": "ALLOWED", "remainingQuota": 5 - len(timestamps)})
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Auth Endpoint
        if path == "/api/v1/auth/login":
            email = payload.get("email", "")
            password = payload.get("password", "")
            if password == "invalid":
                self._send_json(401, {"error": "InvalidCredentials", "message": "Bad email or password"})
                return

            user_id = abs(hash(email)) % 10000 + 100
            token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aerocart_{user_id}_{int(time.time())}"
            self._send_json(200, {
                "accessToken": token,
                "refreshToken": f"ref_{uuid.uuid4().hex[:12]}",
                "expiresIn": 3600,
                "user": {
                    "id": user_id,
                    "email": email,
                    "role": "LEAD_SDET_USER"
                }
            })
            return

        # 2. Order Creation Endpoint (with Dynamic Tenant Isolation vs Shared Collision)
        if path == "/api/v1/orders":
            tenant_id = self.headers.get("X-Test-Tenant-ID")  # May be None (naive mode)
            flight_num = payload.get("flightNumber", "AI-202")
            seat = payload.get("seat", "1A")
            email = payload.get("passengerEmail", "traveler@test.org")

            with STATE_LOCK:
                if tenant_id:
                    # ISOLATED MODE: Every tenant gets dedicated clean inventory
                    tenant_store = TENANT_INVENTORIES.setdefault(tenant_id, {})
                    flight_inv = tenant_store.setdefault(flight_num, {"bookedSeats": set()})
                    booked_set = flight_inv["bookedSeats"]
                    mode = "TENANT_ISOLATED"
                else:
                    # NAIVE / COLLISION MODE: Shares single global inventory
                    flight_inv = GLOBAL_INVENTORY.setdefault(flight_num, {"totalSeats": 10, "bookedSeats": set()})
                    booked_set = flight_inv["bookedSeats"]
                    mode = "GLOBAL_SHARED"

                # Check seat availability
                if seat in booked_set:
                    self._send_json(409, {
                        "error": "SeatAlreadyBooked",
                        "message": f"Seat {seat} on {flight_num} is already occupied!",
                        "mode": mode,
                        "tenantId": tenant_id
                    })
                    return

                booked_set.add(seat)
                order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                order_data = {
                    "orderId": order_id,
                    "flightNumber": flight_num,
                    "seat": seat,
                    "passengerEmail": email,
                    "status": "PENDING",  # Asynchronous saga starts as PENDING
                    "createdAt": time.time(),
                    "tenantId": tenant_id,
                    "isolationMode": mode
                }
                ORDERS[order_id] = order_data

            self._send_json(201, order_data)
            return

        # 3. AI Concierge / RAG Endpoint
        if path == "/api/v1/concierge/chat":
            query = payload.get("query", "").lower()
            mode = payload.get("mode", "grounded")  # "grounded", "hallucinated", "irrelevant"

            # Retrieve matching policy chunk
            matched_chunk = POLICY_CHUNKS[0]
            if "bag" in query or "weight" in query:
                matched_chunk = POLICY_CHUNKS[1]
            elif "delay" in query or "compensation" in query or "eu" in query or "hour" in query:
                matched_chunk = POLICY_CHUNKS[2]

            if mode == "hallucinated":
                answer = "Under all circumstances, basic economy tickets can be canceled for a 100% full cash refund at any time before flight departure with no restrictions."
            elif mode == "irrelevant":
                answer = "Pets traveling in the cabin must remain inside an approved ventilated pet carrier beneath the front seat for the entire duration of the flight."
            else:
                # Grounded answer
                if "cancel" in query or "24" in query:
                    answer = "Under US DOT policy, you can cancel your ticket within 24 hours of booking for a 100% full refund with no fee, provided your flight is at least 7 days away."
                elif "bag" in query:
                    answer = "Transatlantic economy passengers receive 1 free checked bag up to 23kg. A second checked bag incurs an $85 USD fee."
                else:
                    answer = "For flights delayed by 3+ hours arriving at EU destinations, statutory compensation is €250, €400, or €600 based on flight distance."

            self._send_json(200, {
                "query": payload.get("query", ""),
                "answer": answer,
                "retrievedContexts": [matched_chunk["content"]],
                "matchedDocId": matched_chunk["id"],
                "evaluationMode": mode
            })
            return

        # 4. State Reset Endpoint (for test cleanup)
        if path == "/api/v1/admin/reset":
            with STATE_LOCK:
                GLOBAL_INVENTORY.clear()
                GLOBAL_INVENTORY["AI-202"] = {"totalSeats": 10, "bookedSeats": set(), "flightName": "New York -> London"}
                TENANT_INVENTORIES.clear()
                ORDERS.clear()
                RATE_LIMIT_BUCKET.clear()
            self._send_json(200, {"status": "RESET_SUCCESS"})
            return

        self._send_json(404, {"error": "NotFound", "path": path})

    def log_message(self, format, *args):
        # Suppress noisy HTTP logs during fast parallel test execution
        if "DEBUG_AEROCART" in os.environ:
            super().log_message(format, *args)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run_server(port=PORT):
    server = ThreadedHTTPServer(("127.0.0.1", port), AeroCartHandler)
    print(f"🚀 AeroCart Platform running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AeroCart...")
        server.shutdown()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
