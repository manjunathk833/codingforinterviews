"""
Capstone Layer 2/4: Resilient Typed AeroCart API Client (Imports Layer 1 `core`)
File: frameworks/aerocart-quality-suite/clients/aerocart_api_client.py

Goal:
Compose `SuiteConfig` + `WorkerContext` from Layer 1 (`core/config_and_context.py`)
to execute tenant-isolated bookings against `apps.aerocart.server.dispatch_request`,
retry transient 429/503 responses, and poll asynchronous Kafka order confirmation.
"""
import time
from typing import Any, Callable, Dict, List, Optional

from apps.aerocart.server import dispatch_request
from core.config_and_context import SuiteConfig, WorkerContext


class AeroCartApiClient:
    def __init__(
        self,
        ctx: WorkerContext,
        config: Optional[SuiteConfig] = None,
        transport: Callable[..., Dict[str, Any]] = dispatch_request,
    ) -> None:
        self.ctx = ctx
        self.config = config or SuiteConfig()
        self.transport = transport

    def search_flights(self, origin: str = "JFK", destination: str = "LHR") -> List[Dict[str, Any]]:
        """GET `/api/v1/flights/search?from={origin}&to={destination}` and return the `flights` list."""
        raise NotImplementedError("Implement AeroCartApiClient.search_flights()")

    def book_seat(
        self,
        flight_number: str,
        seat: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST `/api/v1/orders` with `self.ctx.build_headers(idempotency_key)` and `self.ctx.isolated_email()`.
        Retry transient HTTP 429 / 503 responses up to `self.config.max_retries` times before returning.
        """
        raise NotImplementedError("Implement AeroCartApiClient.book_seat()")

    def wait_until_confirmed(self, order_id: str, poll_interval_s: float = 0.04) -> Dict[str, Any]:
        """
        Poll GET `/api/v1/orders/{order_id}` until `data['status'] == 'CONFIRMED'`.
        Raise `TimeoutError` if `self.config.timeout_s` elapses first.
        """
        raise NotImplementedError("Implement AeroCartApiClient.wait_until_confirmed()")
