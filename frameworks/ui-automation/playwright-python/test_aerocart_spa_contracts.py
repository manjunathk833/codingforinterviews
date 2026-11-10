"""
Deterministic AeroCart SPA Accessibility Tree, Seat-Selection & Network Route Contract Suite.
Runs 100% locally in <50ms with zero external browser/network flake.
"""

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.aerocart.server import UI_HTML, dispatch_request


class TestAeroCartPlaywrightContracts(unittest.TestCase):
    def setUp(self) -> None:
        dispatch_request("POST", "/api/v1/admin/reset")

    def test_01_spa_accessibility_and_semantic_controls_present(self) -> None:
        """Verify AeroCart SPA exposes accessible labels, button controls, and deterministic seat attributes."""
        self.assertIn('<label for="flight-select">', UI_HTML)
        self.assertIn('id="book-flight-btn"', UI_HTML)
        self.assertIn('data-seat="1A"', UI_HTML)
        self.assertIn('id="order-status-output"', UI_HTML)

    def test_02_isolated_browser_context_booking_journey(self) -> None:
        """Simulate two isolated Playwright BrowserContexts booking identical seat 1A via X-Test-Tenant-ID."""
        ctx_alpha = dispatch_request(
            "POST",
            "/api/v1/orders",
            body={"flightNumber": "AI-202", "seat": "1A", "passengerEmail": "pw_alpha@test.org"},
            headers={"X-Test-Tenant-ID": "pw-worker-1"},
        )
        ctx_beta = dispatch_request(
            "POST",
            "/api/v1/orders",
            body={"flightNumber": "AI-202", "seat": "1A", "passengerEmail": "pw_beta@test.org"},
            headers={"X-Test-Tenant-ID": "pw-worker-2"},
        )
        self.assertEqual(ctx_alpha["status_code"], 201)
        self.assertEqual(ctx_beta["status_code"], 201)
        self.assertEqual(ctx_alpha["data"]["status"], "PENDING")


if __name__ == "__main__":
    unittest.main()
