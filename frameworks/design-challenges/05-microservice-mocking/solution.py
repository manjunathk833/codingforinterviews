"""SDET Challenge: Microservice Mocking & Fault Injection Engine"""
from typing import Dict, List, NamedTuple


class MockResponse(NamedTuple):
    status_code: int
    body: str
    simulated_latency_ms: int


class MicroserviceMockServer:
    def __init__(self):
        self._stubs: Dict[str, MockResponse] = {}
        self._request_history: List[str] = []

    def stub_for(
        self,
        method: str,
        endpoint: str,
        status: int,
        body: str,
        latency_ms: int = 0,
    ) -> None:
        key = f"{method.upper()}:{endpoint}"
        self._stubs[key] = MockResponse(status, body, latency_ms)

    def handle_request(self, method: str, endpoint: str) -> MockResponse:
        key = f"{method.upper()}:{endpoint}"
        self._request_history.append(key)

        if key not in self._stubs:
            return MockResponse(404, '{"error": "Not Found"}', 0)
        return self._stubs[key]

    def verify(self, method: str, endpoint: str, expected_count: int) -> bool:
        key = f"{method.upper()}:{endpoint}"
        actual_count = self._request_history.count(key)
        return actual_count == expected_count


if __name__ == "__main__":
    server = MicroserviceMockServer()

    # Stub endpoint
    server.stub_for("GET", "/inventory/items/42", 200, '{"sku": "42", "stock": 10}', 50)

    # Test 1: Hit stubbed endpoint
    resp1 = server.handle_request("GET", "/inventory/items/42")
    assert resp1.status_code == 200, "Test 1 Failed"
    assert "42" in resp1.body, "Test 1 Failed"
    assert resp1.simulated_latency_ms == 50, "Test 1 Failed"

    # Test 2: Unstubbed endpoint
    resp2 = server.handle_request("GET", "/unknown")
    assert resp2.status_code == 404, "Test 2 Failed"

    # Test 3: Verification
    server.handle_request("GET", "/inventory/items/42")  # 2nd call
    assert server.verify("GET", "/inventory/items/42", 2) is True, "Test 3 Failed"
    assert server.verify("GET", "/unknown", 1) is True, "Test 3 Failed"
    assert server.verify("POST", "/inventory/items/42", 0) is True, "Test 3 Failed"

    print("All 3 Python Microservice Mock Server test cases passed!")
