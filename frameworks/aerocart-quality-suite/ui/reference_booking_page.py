"""Reference Solution — Capstone Layer 3/4: Role-Based UI Booking Page Object & Route Interceptor."""
from typing import Any, Callable, Dict, Optional

from apps.aerocart.server import UI_HTML, dispatch_request
from ui.dom_driver import AeroCartDomSession

try:
    from core.config_and_context import SuiteConfig as _UCfg, WorkerContext as _UCtx
    _UCtx(0, "probe").tenant_id()
    SuiteConfig, WorkerContext = _UCfg, _UCtx
except Exception:
    from core.reference_config_and_context import SuiteConfig, WorkerContext


class AeroCartBookingPage:
    def __init__(
        self,
        ctx: WorkerContext,
        config: Optional[SuiteConfig] = None,
        transport: Callable[..., Dict[str, Any]] = dispatch_request,
    ) -> None:
        self.ctx = ctx
        self.config = (config or SuiteConfig()).validate()
        self.dom = AeroCartDomSession(UI_HTML, transport)

    def choose_seat(self, seat_code: str) -> None:
        seat = self.dom.seats.get(seat_code)
        if not seat:
            raise ValueError(f"Unknown seat {seat_code}")
        if "booked" in seat["classes"]:
            raise ValueError(f"Seat {seat_code} is already booked")
        self.dom.selected_seat = seat_code

    def fill_passenger_email(self, email: Optional[str] = None) -> str:
        chosen = (email or self.ctx.isolated_email()).strip()
        if "@" not in chosen:
            raise ValueError("Invalid passenger email")
        self.dom.by_id["passenger-email"]["value"] = chosen
        return chosen

    def mock_orders_fault(self, status_code: int = 503, error_code: str = "UpstreamOutage") -> None:
        self.dom.intercept_route("/api/v1/orders", status_code, {"error": error_code})

    def submit_booking(self) -> Dict[str, Any]:
        btn_id = self.dom.buttons_by_text.get("Confirm Booking")
        if btn_id != "book-flight-btn":
            raise RuntimeError("Confirm Booking button missing from DOM")
        flight = self.dom.by_id["flight-select"]["value"]
        email = self.dom.by_id["passenger-email"]["value"] or self.fill_passenger_email()
        resp = self.dom.fetch_json(
            "POST",
            "/api/v1/orders",
            body={
                "flightNumber": flight,
                "seat": self.dom.selected_seat,
                "passengerEmail": email,
            },
            headers=self.ctx.build_headers(),
        )
        status_el = self.dom.by_id["order-status-output"]
        if resp["status_code"] == 201:
            status_el["text"] = f"Order Created: {resp['data'].get('orderId')}"
        else:
            status_el["text"] = f"Booking Error ({resp['status_code']}): {resp['data'].get('error', 'Failed')}"
        return resp
