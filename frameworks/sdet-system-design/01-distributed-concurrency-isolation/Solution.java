import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/**
 * Architecture Kata 01: Dynamic Tenant Key Partitioning (Java 17 Workspace).
 *
 * Goal:
 * 1. Make 32 parallel worker threads succeed simultaneously when booking Seat 1A on Flight AI-202.
 * 2. Eliminate HTTP 409 Conflict race conditions without truncating shared database tables.
 */
public class Solution {

    /**
     * Thread-safe in-memory simulation of the AeroCart Order Inventory engine.
     * Mirrors the exact partitioning logic of apps/aerocart/server.py.
     */
    static class AeroCartInventoryEngine {
        private final Set<String> globalSharedSeats = ConcurrentHashMap.newKeySet();
        private final Map<String, Set<String>> tenantIsolatedSeats = new ConcurrentHashMap<>();

        public synchronized int bookSeat(String flightNumber, String seat, String tenantId) {
            String key = flightNumber + ":" + seat;
            if (tenantId == null || tenantId.isBlank()) {
                // Naive global shared mode: only first thread succeeds; others get 409 Conflict
                if (!globalSharedSeats.add(key)) {
                    return 409;
                }
                return 201;
            } else {
                // Tenant-isolated mode: each unique X-Test-Tenant-ID gets an isolated partition
                Set<String> partition = tenantIsolatedSeats.computeIfAbsent(
                        tenantId, k -> ConcurrentHashMap.newKeySet()
                );
                if (!partition.add(key)) {
                    return 409;
                }
                return 201;
            }
        }
    }

    /**
     * Candidate Workspace: Return a cryptographically unique tenant header value for each worker,
     * or implement runIsolatedWorker() to pass 32/32 concurrent bookings.
     */
    public static int runIsolatedWorker(int workerId, AeroCartInventoryEngine engine) {
        // Ephemeral cryptographic tenant context per worker thread
        String tenantKey = "tenant_worker_" + workerId + "_" + UUID.randomUUID().toString().substring(0, 8);
        return engine.bookSeat("AI-202", "1A", tenantKey);
    }

    public static void main(String[] args) throws Exception {
        final int numWorkers = 32;
        AeroCartInventoryEngine engine = new AeroCartInventoryEngine();
        ExecutorService pool = Executors.newFixedThreadPool(numWorkers);

        // 1. Verify Naive Shared Mode reproduces the 31/32 HTTP 409 Conflict race condition
        List<Callable<Integer>> naiveTasks = new ArrayList<>();
        for (int i = 1; i <= numWorkers; i++) {
            naiveTasks.add(() -> engine.bookSeat("AI-202", "1A", null));
        }
        List<Future<Integer>> naiveFutures = pool.invokeAll(naiveTasks);
        int naivePassed = 0;
        int naiveConflicts = 0;
        for (Future<Integer> f : naiveFutures) {
            int status = f.get();
            if (status == 201) naivePassed++;
            else if (status == 409) naiveConflicts++;
        }
        assert naivePassed == 1 && naiveConflicts == 31
                : "Expected 1 pass and 31 conflicts in naive mode, got " + naivePassed + " / " + naiveConflicts;

        // 2. Verify Tenant-Isolated Mode passes 32/32 concurrent workers with 0 conflicts
        List<Callable<Integer>> isolatedTasks = new ArrayList<>();
        for (int i = 1; i <= numWorkers; i++) {
            final int workerId = i;
            isolatedTasks.add(() -> runIsolatedWorker(workerId, engine));
        }
        List<Future<Integer>> isolatedFutures = pool.invokeAll(isolatedTasks);
        int isolatedPassed = 0;
        for (Future<Integer> f : isolatedFutures) {
            if (f.get() == 201) isolatedPassed++;
        }
        pool.shutdown();

        assert isolatedPassed == numWorkers
                : "Expected all 32 parallel isolated workers to return 201 Created, got " + isolatedPassed;

        System.out.println("All 32 Java Distributed Concurrency & Tenant Isolation test cases passed!");
    }
}

