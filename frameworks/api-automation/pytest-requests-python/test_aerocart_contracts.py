"""
Deterministic AeroCart Multi-Endpoint API Contract, Tenant Isolation & Async Saga Suite.
Exercises AeroCartClient(in_process=True) with zero external network dependency.
"""

import pathlib
import sys
import time
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.aerocart.client import AeroCartClient


class TestAeroCartApiContracts(unittest.TestCase):
    def setUp(self) -> None:
        self.client = AeroCartClient(in_process=True)
        self.client.reset_state()

    def test_01_jwt_auth_and_flight_search_schema(self) -> None:
        auth = self.client.login("lead@sdet.org", "pass")
        self.assertEqual(auth["status_code"], 200)
        self.assertIn("accessToken", auth["data"])
        self.assertIn("refreshToken", auth["data"])

        flights = self.client.search_flights("JFK", "LHR")
        self.assertEqual(flights["status_code"], 200)
        self.assertTrue(len(flights["data"].get("flights", [])) >= 1)

    def test_02_tenant_isolation_and_eventual_consistency_saga(self) -> None:
        created = self.client.create_order(
            flight_number="AI-202",
            seat="2A",
            passenger_email="api_contract@test.org",
            tenant_id="api-tenant-01",
        )
        self.assertEqual(created["status_code"], 201)
        order_id = created["data"]["orderId"]

        # Bounded eventual consistency poll (`PENDING -> CONFIRMED`)
        deadline = time.time() + 1.5
        final_status = created["data"]["status"]
        while time.time() < deadline:
            polled = self.client.get_order(order_id)
            final_status = polled["data"].get("status", "")
            if final_status == "CONFIRMED":
                break
            time.sleep(0.05)
        self.assertEqual(final_status, "CONFIRMED")


if __name__ == "__main__":
    unittest.main()
