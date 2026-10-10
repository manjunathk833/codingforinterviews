package com.maang.framework.concurrency;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.*;

/**
 * Architecture Kata 01 (Java 17): Dynamic Tenant Key Partitioning
 * 
 * Goal:
 * Execute 32 parallel worker threads booking Seat '1A' simultaneously on Flight 'AI-202'.
 * Eliminate all HTTP 409 Conflict race conditions using dynamic tenant isolation.
 */
public class Solution {

    private static final String BASE_URL = "http://127.0.0.1:8993";

    public record WorkerResult(int workerId, int statusCode, String tenantId, String orderId) {}

    // =========================================================================
    // ✍️ CANDIDATE IMPLEMENTATION AREA
    // =========================================================================
    public static WorkerResult runIsolatedWorker(int workerId) throws Exception {
        /*
         * TODO: Implement Dynamic Tenant Isolation for this worker thread.
         * 
         * Requirements:
         * 1. Generate an ephemeral UUID tenant key: "tenant_java_" + workerId + "_" + UUID.randomUUID()
         * 2. Construct JSON payload: {"flightNumber": "AI-202", "seat": "1A", "passengerEmail": "..."}
         * 3. Send HTTP POST to BASE_URL + "/api/v1/orders"
         * 4. Inject request header: "X-Test-Tenant-ID" -> tenantKey
         * 5. Read response status and return new WorkerResult(...)
         */
        
        // ---------------------------------------------------------------------
        // UNCOMMENT AND IMPLEMENT YOUR CODE HERE:
        // ---------------------------------------------------------------------
        String tenantKey = "tenant_java_" + workerId + "_" + UUID.randomUUID().toString().substring(0, 8);
        String payload = String.format(
            "{\"flightNumber\":\"AI-202\",\"seat\":\"1A\",\"passengerEmail\":\"sdet_%d@testvault.org\"}",
            workerId
        );

        URL url = new URL(BASE_URL + "/api/v1/orders");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("X-Test-Tenant-ID", tenantKey); // 🔑 DYNAMIC TENANT ISOLATION
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(payload.getBytes(StandardCharsets.UTF_8));
        }

        int statusCode = conn.getResponseCode();
        return new WorkerResult(workerId, statusCode, tenantKey, "ORD-CONFIRMED");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("======================================================================");
        System.out.println("☕ JAVA 17: Verifying Dynamic Tenant Isolation Across 32 Threads");
        System.out.println("======================================================================");

        int numWorkers = 32;
        ExecutorService executor = Executors.newFixedThreadPool(numWorkers);
        List<Future<WorkerResult>> futures = new ArrayList<>();

        long startTime = System.currentTimeMillis();
        for (int i = 1; i <= numWorkers; i++) {
            final int id = i;
            futures.add(executor.submit(() -> runIsolatedWorker(id)));
        }

        List<WorkerResult> results = new ArrayList<>();
        for (Future<WorkerResult> f : futures) {
            results.add(f.get());
        }
        executor.shutdown();
        long elapsed = System.currentTimeMillis() - startTime;

        long passed = results.stream().filter(r -> r.statusCode() == 201).count();
        long failed = results.stream().filter(r -> r.statusCode() != 201).count();

        System.out.printf("%n📊 RESULTS: %d Passed (201 Created) | %d Failed (Elapsed: %dms)%n", passed, failed, elapsed);
        
        if (passed == numWorkers && failed == 0) {
            System.out.println("🏆 Java 17 Dynamic Tenant Isolation test passed with 100% success!");
        } else {
            System.out.printf("❌ Verification Failed: %d workers failed.%n", failed);
            System.exit(1);
        }
    }
}
