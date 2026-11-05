import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Databases Lab 01: Bounded WAL Ring-Buffer & Optimistic Concurrency Control (Java 17).
 */
public class Solution {

    static class BoundedWalRingBuffer {
        private final int maxCapacity;
        private final Deque<String> queue = new ArrayDeque<>();
        private int evictedCount = 0;

        public BoundedWalRingBuffer(int maxCapacity) {
            this.maxCapacity = maxCapacity;
        }

        public void appendEvent(String eventId) {
            if (queue.size() >= maxCapacity) {
                queue.pollFirst();
                evictedCount++;
            }
            queue.addLast(eventId);
        }

        public List<String> drainAll() {
            List<String> out = new ArrayList<>(queue);
            queue.clear();
            return out;
        }

        public int getEvictedCount() {
            return evictedCount;
        }
    }

    static class OptimisticVersionStore {
        public record VersionedRow(String value, int version) {}

        private final Map<String, VersionedRow> store = new HashMap<>();

        public int putInitial(String key, String value) {
            store.put(key, new VersionedRow(value, 1));
            return 1;
        }

        public boolean compareAndSwap(String key, int expectedVersion, String newValue) {
            VersionedRow current = store.get(key);
            if (current == null || current.version() != expectedVersion) {
                return false;
            }
            store.put(key, new VersionedRow(newValue, current.version() + 1));
            return true;
        }

        public VersionedRow read(String key) {
            return store.get(key);
        }
    }

    public static void main(String[] args) {
        BoundedWalRingBuffer wal = new BoundedWalRingBuffer(3);
        for (int i = 1; i <= 5; i++) {
            wal.appendEvent("evt_" + i);
        }
        assert wal.getEvictedCount() == 2 : "Expected 2 evicted events";
        assert List.of("evt_3", "evt_4", "evt_5").equals(wal.drainAll()) : "Unexpected retained WAL order";

        OptimisticVersionStore store = new OptimisticVersionStore();
        int v1 = store.putInitial("seat_1A", "AVAILABLE");
        boolean workerA = store.compareAndSwap("seat_1A", v1, "BOOKED_BY_A");
        boolean workerB = store.compareAndSwap("seat_1A", v1, "BOOKED_BY_B");

        assert workerA : "Worker A should succeed";
        assert !workerB : "Worker B with stale version must be rejected";
        assert store.read("seat_1A").version() == 2 : "Expected version 2";

        System.out.println("All 3 Java Database WAL Ring-Buffer & OCC Isolation test cases passed!");
    }
}

