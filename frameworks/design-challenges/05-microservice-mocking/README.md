# CH-05: Microservice Mocking & Fault Injection Engine

- **Target Level**: Staff SDET / Chaos & Resilience Engineering (Netflix, Amazon, Google)
- **Domain**: Microservice Mocking, Latency Simulation & Fault Injection

---

## Interview Problem Statement
In distributed architectures, testing resilience requires verifying how upstream services behave when downstream microservices experience simulated network latency, error status codes, or intermittent drop-outs.

Your task is to implement an in-memory **Microservice Mock Server**:
1. Supports registering path stubs with expected HTTP methods (e.g. `stubFor("GET", "/inventory/items", status, body)`).
2. Supports **Fault Injection**:
   - Simulated latency delay (ms).
   - Error injection rate (e.g. 50% probability of throwing `500 Internal Server Error`).
3. Supports **Request Verification**:
   - `verify(method, path, times)`: Asserts that an endpoint was invoked exactly `times` count.

---

## Target Complexities
- **Time Complexity**: $O(1)$ per stub match and invocation
- **Space Complexity**: $O(S)$ where $S$ is number of registered stubs and request logs
