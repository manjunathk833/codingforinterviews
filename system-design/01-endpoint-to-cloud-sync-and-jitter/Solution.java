import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

/**
 * System Design Lab 01: Endpoint-to-Cloud Sync, Full Jitter & Idempotent Ingestion (Java 17).
 */
public class Solution {

    public record StormResult(int windowSec, int naivePeakRps, int jitterPeakRps, double peakReductionPct) {}

    public record Batch(String idempotencyKey, List<String> events) {}

    public record IngestResult(int uniqueBatches, int committedEvents, int duplicatesDropped) {}

    public StormResult simulateReconnectionStorm(int numEndpoints, int attempt, int baseSec, int maxCapSec, long seed) {
        Random rng = new Random(seed);
        int window = Math.min(maxCapSec, baseSec * (1 << attempt));

        int naivePeakRps = numEndpoints; // All endpoints fire at exact same second `window`
        Map<Integer, Integer> jitterBuckets = new HashMap<>();
        int jitterPeakRps = 0;

        for (int i = 0; i < numEndpoints; i++) {
            int sec = rng.nextInt(window + 1);
            int count = jitterBuckets.getOrDefault(sec, 0) + 1;
            jitterBuckets.put(sec, count);
            if (count > jitterPeakRps) {
                jitterPeakRps = count;
            }
        }

        double reductionPct = Math.round((1.0 - (jitterPeakRps / (double) naivePeakRps)) * 1000.0) / 10.0;
        return new StormResult(window, naivePeakRps, jitterPeakRps, reductionPct);
    }

    public IngestResult ingestIdempotentBatches(List<Batch> batches) {
        Set<String> seen = new HashSet<>();
        int committed = 0;
        int dropped = 0;
        for (Batch b : batches) {
            if (seen.add(b.idempotencyKey())) {
                committed += b.events().size();
            } else {
                dropped++;
            }
        }
        return new IngestResult(seen.size(), committed, dropped);
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        StormResult storm = sol.simulateReconnectionStorm(1000, 3, 2, 60, 42L);
        assert storm.naivePeakRps() == 1000 : "Expected 1000 naive peak";
        assert storm.jitterPeakRps() < 120 : "Expected jitter peak < 120, got " + storm.jitterPeakRps();
        assert storm.peakReductionPct() > 85.0 : "Expected >85% reduction";

        List<Batch> batches = List.of(
                new Batch("batch-uuid-01", List.of("usb_mount", "file_open")),
                new Batch("batch-uuid-01", List.of("usb_mount", "file_open")),
                new Batch("batch-uuid-02", List.of("tls_handshake"))
        );
        IngestResult ingest = sol.ingestIdempotentBatches(batches);
        assert ingest.uniqueBatches() == 2 && ingest.committedEvents() == 3 && ingest.duplicatesDropped() == 1;

        System.out.println("All 2 Java Endpoint-to-Cloud Sync, Full Jitter & Idempotency test cases passed!");
    }
}

