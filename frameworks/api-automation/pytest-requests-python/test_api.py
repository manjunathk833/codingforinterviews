"""API Automation Suite Tests demonstrating contract validation, status checks, and latency benchmarking."""
import unittest
from api_client import BaseApiClient, ApiResponse


class DummyMockClient(BaseApiClient):
    """Client that simulates network responses for offline/sandboxed execution."""

    def request(self, method: str, endpoint: str, payload=None, headers=None) -> ApiResponse:
        if endpoint == "users/1":
            return ApiResponse(
                status_code=200,
                body={"id": 1, "name": "Manjunath", "role": "Senior SDET", "active": True},
                headers={"Content-Type": "application/json"},
                latency_ms=45.2,
            )
        elif endpoint == "users" and method == "POST":
            return ApiResponse(
                status_code=201,
                body={"id": 101, "name": payload.get("name"), "created": True},
                headers={"Content-Type": "application/json"},
                latency_ms=62.1,
            )
        return ApiResponse(status_code=404, body={"error": "Not Found"}, headers={}, latency_ms=10.0)


class TestUserApi(unittest.TestCase):
    def setUp(self):
        self.client = DummyMockClient("https://api.example.com")

    def test_get_user_success(self):
        resp = self.client.request("GET", "users/1")
        self.assertTrue(resp.is_success)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body["name"], "Manjunath")
        self.assertLess(resp.latency_ms, 500, "Latency benchmark violated (>500ms)")

    def test_create_user_contract(self):
        payload = {"name": "Alex", "role": "Engineer"}
        resp = self.client.request("POST", "users", payload=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.body["id"], 101)
        self.assertTrue(resp.body["created"])

    def test_user_not_found(self):
        resp = self.client.request("GET", "users/9999")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
