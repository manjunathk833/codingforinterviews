package core.specs;

import java.util.HashMap;
import java.util.Map;

/**
 * Factory for creating standardized Request Specifications.
 */
public class RequestSpecFactory {

    private String baseUri;
    private final Map<String, String> headers = new HashMap<>();

    public RequestSpecFactory() {
        this.baseUri = "https://api.internal.service/v1";
        this.headers.put("Content-Type", "application/json");
        this.headers.put("Accept", "application/json");
    }

    public RequestSpecFactory setBaseUri(String baseUri) {
        this.baseUri = baseUri;
        return this;
    }

    public RequestSpecFactory addHeader(String key, String value) {
        this.headers.put(key, value);
        return this;
    }

    public RequestSpecFactory withBearerToken(String token) {
        this.headers.put("Authorization", "Bearer " + token);
        return this;
    }

    public String getBaseUri() {
        return baseUri;
    }

    public Map<String, String> getHeaders() {
        return headers;
    }

    public static RequestSpecFactory defaultSpec() {
        return new RequestSpecFactory();
    }
}
