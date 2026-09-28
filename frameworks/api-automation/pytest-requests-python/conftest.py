"""Pytest configuration and reusable fixtures for API testing."""
from api_client import BaseApiClient, ApiResponse


class MockApiClient(BaseApiClient):
    """Offline test double for sandboxed test execution."""

    def request(self, method: str, endpoint: str, payload=None, headers=None) -> ApiResponse:
        if endpoint == "users/1":
            return ApiResponse(
                status_code=200,
                body={
                    "id": 1,
                    "name": "Manjunath H K",
                    "email": "manjunathhk833@gmail.com",
                    "role": "SENIOR_SDET",
                    "active": True,
                },
                headers={"Content-Type": "application/json"},
                latency_ms=28.4,
            )
        elif endpoint == "users" and method == "POST":
            return ApiResponse(
                status_code=201,
                body={
                    "id": 102,
                    "name": payload.get("name", "New User"),
                    "email": payload.get("email", "newuser@example.com"),
                    "role": payload.get("role", "SDET"),
                    "active": True,
                },
                headers={"Content-Type": "application/json"},
                latency_ms=45.1,
            )
        return ApiResponse(status_code=404, body={"error": "Not Found"}, headers={}, latency_ms=10.0)


def get_api_client():
    """Provides a configured API client."""
    return MockApiClient(base_url="https://api.internal.service/v1")
