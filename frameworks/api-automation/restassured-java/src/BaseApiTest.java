package src;

import java.util.HashMap;
import java.util.Map;

/**
 * Architectural demonstration of Enterprise Request/Response Specification Builder Pattern.
 */
public class BaseApiTest {

    public static class RequestSpec {
        private String baseUrl;
        private Map<String, String> headers = new HashMap<>();

        public RequestSpec setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }

        public RequestSpec addHeader(String key, String value) {
            this.headers.put(key, value);
            return this;
        }

        public RequestSpec addBearerAuth(String token) {
            this.headers.put("Authorization", "Bearer " + token);
            return this;
        }

        public String getBaseUrl() {
            return baseUrl;
        }

        public Map<String, String> getHeaders() {
            return headers;
        }
    }

    public static class SpecFactory {
        public static RequestSpec defaultJsonSpec() {
            return new RequestSpec()
                    .setBaseUrl("https://api.internal.service/v1")
                    .addHeader("Content-Type", "application/json")
                    .addHeader("Accept", "application/json");
        }
    }

    public static void main(String[] args) {
        RequestSpec spec = SpecFactory.defaultJsonSpec().addBearerAuth("sample_jwt_token_123");

        assert spec.getBaseUrl().equals("https://api.internal.service/v1") : "Base URL incorrect";
        assert spec.getHeaders().get("Authorization").equals("Bearer sample_jwt_token_123") : "Auth header missing";
        assert spec.getHeaders().get("Content-Type").equals("application/json") : "Content-Type header missing";

        System.out.println("BaseApiTest spec assertions passed successfully!");
    }
}
