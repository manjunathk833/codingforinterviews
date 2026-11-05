import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.NavigableMap;
import java.util.TreeMap;
import java.util.zip.CRC32;

/**
 * System Design Lab 02: Consistent Hashing Ring with Virtual Nodes (Java 17).
 */
public class Solution {

    static class ConsistentHashRing {
        private final int vnodesPerNode;
        private final NavigableMap<Long, String> ring = new TreeMap<>();

        public ConsistentHashRing(List<String> nodes, int vnodesPerNode) {
            this.vnodesPerNode = vnodesPerNode;
            for (String n : nodes) {
                addNode(n);
            }
        }

        private long hash(String key) {
            CRC32 crc = new CRC32();
            crc.update(key.getBytes(StandardCharsets.UTF_8));
            return crc.getValue();
        }

        public void addNode(String node) {
            for (int v = 0; v < vnodesPerNode; v++) {
                ring.put(hash(node + "#vnode" + v), node);
            }
        }

        public void removeNode(String node) {
            for (int v = 0; v < vnodesPerNode; v++) {
                long h = hash(node + "#vnode" + v);
                if (node.equals(ring.get(h))) {
                    ring.remove(h);
                }
            }
        }

        public String getNode(String key) {
            if (ring.isEmpty()) {
                throw new IllegalStateException("Ring is empty");
            }
            long h = hash(key);
            Map.Entry<Long, String> entry = ring.ceilingEntry(h);
            if (entry == null) {
                entry = ring.firstEntry();
            }
            return entry.getValue();
        }
    }

    public static void main(String[] args) {
        List<String> nodes = List.of("worker-node-1", "worker-node-2", "worker-node-3", "worker-node-4");
        ConsistentHashRing ring = new ConsistentHashRing(nodes, 64);

        Map<String, String> before = new HashMap<>();
        Map<String, Integer> counts = new HashMap<>();
        for (int i = 0; i < 400; i++) {
            String key = "test_suite_" + i;
            String target = ring.getNode(key);
            before.put(key, target);
            counts.put(target, counts.getOrDefault(target, 0) + 1);
        }

        for (String n : nodes) {
            assert counts.getOrDefault(n, 0) > 40 : "Expected balanced load on " + n;
        }

        ring.removeNode("worker-node-4");
        int moved = 0;
        for (int i = 0; i < 400; i++) {
            String key = "test_suite_" + i;
            String prev = before.get(key);
            String curr = ring.getNode(key);
            if (!prev.equals(curr)) {
                moved++;
                assert "worker-node-4".equals(prev) : "Healthy node key moved unexpectedly!";
            }
        }
        double ratio = moved / 400.0;
        assert ratio >= 0.15 && ratio <= 0.38 : "Expected ~25% keys moved, got " + ratio;

        System.out.println("All 2 Java Consistent Hashing Ring & Virtual Node Sharding test cases passed!");
    }
}

