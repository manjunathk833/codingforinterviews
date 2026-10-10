"""
AeroCart Unified Test Client.
Supports both live HTTP socket execution and in-process direct dispatch.
Allows tests to run natively in CI, parallel workers, and sandboxed environments.
"""

import json
import urllib.request
import urllib.error
import time
from typing import Dict, Any, Optional

class AeroCartClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", in_process: bool = False):
        self.base_url = base_url.rstrip("/")
        self.in_process = in_process

    def _http_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        payload_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=payload_bytes, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
                return {
                    "status_code": resp.status,
                    "data": json.loads(body) if body else {},
                    "headers": dict(resp.headers)
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return {
                "status_code": e.code,
                "data": json.loads(err_body) if err_body else {},
                "headers": dict(e.headers)
            }

    def login(self, email: str = "lead@sdet.org", password: str = "pass") -> Dict[str, Any]:
        return self._http_request("POST", "/api/v1/auth/login", {"email": email, "password": password})

    def search_flights(self, origin: str = "JFK", destination: str = "LHR") -> Dict[str, Any]:
        return self._http_request("GET", f"/api/v1/flights/search?from={origin}&to={destination}")

    def create_order(self, flight_number: str = "AI-202", seat: str = "1A", passenger_email: str = "traveler@test.org", tenant_id: Optional[str] = None) -> Dict[str, Any]:
        headers = {}
        if tenant_id:
            headers["X-Test-Tenant-ID"] = tenant_id
        return self._http_request("POST", "/api/v1/orders", {
            "flightNumber": flight_number,
            "seat": seat,
            "passengerEmail": passenger_email
        }, headers=headers)

    def get_order(self, order_id: str) -> Dict[str, Any]:
        return self._http_request("GET", f"/api/v1/orders/{order_id}")

    def ask_concierge(self, query: str, mode: str = "grounded") -> Dict[str, Any]:
        return self._http_request("POST", "/api/v1/concierge/chat", {"query": query, "mode": mode})

    def trigger_latency(self, delay_ms: int = 1000) -> Dict[str, Any]:
        return self._http_request("GET", f"/api/v1/chaos/latency?ms={delay_ms}")

    def reset_state(self) -> Dict[str, Any]:
        return self._http_request("POST", "/api/v1/admin/reset")
