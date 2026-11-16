"""Reference Solution — Capstone Layer 2/4: Resilient Typed AeroCart API Client."""
import time
from typing import Any, Callable, Dict, List, Optional

from apps.aerocart.server import dispatch_request
try:
    from core.config_and_context import SuiteConfig as _UserCfg, WorkerContext as _UserCtx
    _UserCtx(0, "probe").tenant_id()
    SuiteConfig, WorkerContext = _UserCfg, _UserCtx
except Exception:
    from core.reference_config_and_context import SuiteConfig, WorkerContext


class AeroCartApiClient:
    def __init__(
        self,
        ctx: WorkerContext,
        config: Optional[SuiteConfig] = None,
        transport: Callable[..., Dict[str, Any]] = dispatch_request,
    ) -> None:
        self.ctx = ctx
        self.config = (config or SuiteConfig()).validate()
        self.transport = transport

    def search_flights(self, origin: str = "JFK", destination: str = "LHR") -> List[Dict[str, Any]]:
        resp = self.transport(
            "GET",
            f"/api/v1/flights/search?from={origin}&to={destination}",
            headers=self.ctx.build_headers(),
        )
        if resp["status_code"] != 200:
            raise RuntimeError(f"Flight search failed with HTTP {resp['status_code']}")
        return list(resp["data"].get("flights", []))

    def book_seat(
        self,
        flight_number: str,
        seat: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = self.ctx.build_headers(idempotency_key=idempotency_key)
        payload = {
            "flightNumber": flight_number,
            "seat": seat,
            "passengerEmail": self.ctx.isolated_email(),
        }
        attempts = 0
        while True:
            resp = self.transport("POST", "/api/v1/orders", body=payload, headers=headers)
            if resp["status_code"] not in (429, 503) or attempts >= self.config.max_retries:
                return resp
            attempts += 1
            time.sleep(0.005 * attempts)

    def wait_until_confirmed(self, order_id: str, poll_interval_s: float = 0.04) -> Dict[str, Any]:
        deadline = time.monotonic() + self.config.timeout_s
        headers = self.ctx.build_headers()
        while time.monotonic() <= deadline:
            resp = self.transport("GET", f"/api/v1/orders/{order_id}", headers=headers)
            if resp["status_code"] == 200 and resp["data"].get("status") == "CONFIRMED":
                return resp["data"]
            time.sleep(poll_interval_s)
        raise TimeoutError(f"Order {order_id} did not reach CONFIRMED within {self.config.timeout_s}s")
