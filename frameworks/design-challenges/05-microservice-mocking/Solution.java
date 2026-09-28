import java.util.*;

/**
 * SDET Challenge: Microservice Mocking & Fault Injection Engine
 */
public class Solution {

    public static class MockResponse {
        public final int statusCode;
        public final String body;
        public final long simulatedLatencyMs;

        public MockResponse(int statusCode, String body, long simulatedLatencyMs) {
            this.statusCode = statusCode;
            this.body = body;
            this.simulatedLatencyMs = simulatedLatencyMs;
        }
    }

    public static class MicroserviceMockServer {
        private final Map<String, MockResponse> stubs = new HashMap<>();
        private final List<String> requestHistory = new ArrayList<>();

        public void stubFor(String method, String endpoint, int status, String body, long latencyMs) {
            String key = method.toUpperCase() + ":" + endpoint;
            stubs.put(key, new MockResponse(status, body, latencyMs));
        }

        public MockResponse handleRequest(String method, String endpoint) {
            String key = method.toUpperCase() + ":" + endpoint;
            requestHistory.add(key);

            if (!stubs.containsKey(key)) {
                return new MockResponse(404, "{\"error\": \"Not Found\"}", 0);
            }
            return stubs.get(key);
        }

        public boolean verify(String method, String endpoint, int expectedCount) {
            String key = method.toUpperCase() + ":" + endpoint;
            int count = 0;
            for (String req : requestHistory) {
                if (req.equals(key)) count++;
            }
            return count == expectedCount;
        }
    }

    public static void main(String[] args) {
        MicroserviceMockServer server = new MicroserviceMockServer();

        // Register stub with simulated latency
        server.stubFor("GET", "/inventory/items/42", 200, "{\"sku\": \"42\", \"stock\": 10}", 50);

        // Test 1: Hit stubbed endpoint
        MockResponse resp1 = server.handleRequest("GET", "/inventory/items/42");
        assert resp1.statusCode == 200 : "Test 1 Failed: Expected status 200";
        assert resp1.body.contains("42") : "Test 1 Failed: Body missing SKU";
        assert resp1.simulatedLatencyMs == 50 : "Test 1 Failed: Latency incorrect";

        // Test 2: Unstubbed endpoint returns 404
        MockResponse resp2 = server.handleRequest("GET", "/unknown");
        assert resp2.statusCode == 404 : "Test 2 Failed: Expected status 404";

        // Test 3: Verification of invocation counts
        server.handleRequest("GET", "/inventory/items/42"); // 2nd call
        assert server.verify("GET", "/inventory/items/42", 2) : "Test 3 Failed: Expected count 2";
        assert server.verify("GET", "/unknown", 1) : "Test 3 Failed: Expected count 1";
        assert server.verify("POST", "/inventory/items/42", 0) : "Test 3 Failed: Expected count 0";

        System.out.println("All 3 Java Microservice Mock Server test cases passed!");
    }
}
