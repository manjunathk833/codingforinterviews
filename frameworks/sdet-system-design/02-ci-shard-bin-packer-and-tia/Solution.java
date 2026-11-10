import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.Set;

/**
 * SDET System Design Lab 02: LPT CI Shard Bin-Packer & AST Test Impact Analysis (Java 17).
 */
public class Solution {

    record SpecTiming(String name, double seconds) {}
    record ShardState(double load, int index) {}

    static double lptMakespan(List<SpecTiming> specs, int numShards) {
        List<SpecTiming> sorted = new ArrayList<>(specs);
        sorted.sort(Comparator.comparingDouble(SpecTiming::seconds).reversed().thenComparing(SpecTiming::name));

        PriorityQueue<ShardState> pq = new PriorityQueue<>(
            Comparator.comparingDouble(ShardState::load).thenComparingInt(ShardState::index)
        );
        for (int i = 0; i < numShards; i++) {
            pq.offer(new ShardState(0.0, i));
        }
        for (SpecTiming spec : sorted) {
            ShardState minShard = pq.poll();
            pq.offer(new ShardState(minShard.load() + spec.seconds(), minShard.index()));
        }
        double maxLoad = 0.0;
        for (ShardState st : pq) {
            maxLoad = Math.max(maxLoad, st.load());
        }
        return maxLoad;
    }

    static Set<String> selectImpactedTests(
            List<String> changedFiles,
            Map<String, List<String>> reverseGraph,
            Set<String> allTests) {
        Set<String> globalTriggers = Set.of("pyproject.toml", "conftest.py", ".github/workflows/ci.yml");
        for (String f : changedFiles) {
            if (globalTriggers.contains(f)) {
                return new HashSet<>(allTests);
            }
        }
        Set<String> visited = new HashSet<>(changedFiles);
        Queue<String> queue = new ArrayDeque<>(changedFiles);
        Set<String> impacted = new HashSet<>();
        while (!queue.isEmpty()) {
            String curr = queue.poll();
            if (allTests.contains(curr)) {
                impacted.add(curr);
            }
            for (String dep : reverseGraph.getOrDefault(curr, List.of())) {
                if (visited.add(dep)) {
                    queue.offer(dep);
                }
            }
        }
        return impacted;
    }

    public static void main(String[] args) {
        List<SpecTiming> skewed = List.of(
            new SpecTiming("01_heavy_checkout.py", 180.0),
            new SpecTiming("02_fast_unit.py", 10.0),
            new SpecTiming("03_fast_lint.py", 10.0),
            new SpecTiming("04_heavy_payments.py", 175.0),
            new SpecTiming("05_fast_schema.py", 15.0),
            new SpecTiming("06_fast_util.py", 15.0),
            new SpecTiming("07_heavy_concierge.py", 165.0),
            new SpecTiming("08_medium_api.py", 45.0),
            new SpecTiming("09_medium_auth.py", 45.0)
        );
        double lpt = lptMakespan(skewed, 3);
        assert lpt <= 235.0 : "Expected LPT makespan <= 235s, got " + lpt;

        Map<String, List<String>> rev = Map.of(
            "pricing/tax.py", List.of("checkout/cart.py"),
            "checkout/cart.py", List.of("tests/test_cart.py", "tests/test_checkout_e2e.py"),
            "concierge/rag.py", List.of("tests/test_concierge.py")
        );
        Set<String> allTests = Set.of("tests/test_cart.py", "tests/test_checkout_e2e.py", "tests/test_concierge.py");
        Set<String> sel = selectImpactedTests(List.of("pricing/tax.py"), rev, allTests);
        assert sel.equals(Set.of("tests/test_cart.py", "tests/test_checkout_e2e.py"));
        assert selectImpactedTests(List.of("conftest.py"), rev, allTests).equals(allTests);

        System.out.println("All 3 Java LPT CI Shard Bin-Packer & AST Test Impact Analysis test cases passed!");
    }
}
