import java.util.*;

/**
 * SDET Challenge: Deep JSON Payload Diff Engine
 */
public class Solution {

    public static class DiffResult {
        public final List<String> differences = new ArrayList<>();

        public void addDiff(String path, Object expected, Object actual) {
            differences.add(String.format("Path '%s': expected [%s], but got [%s]", path, expected, actual));
        }

        public boolean hasDifferences() {
            return !differences.isEmpty();
        }
    }

    /**
     * Recursively compares two JSON-like nested Map/List structures.
     */
    @SuppressWarnings("unchecked")
    public DiffResult compare(Object expected, Object actual, Set<String> ignorePaths) {
        DiffResult result = new DiffResult();
        compareInternal("", expected, actual, ignorePaths, result);
        return result;
    }

    @SuppressWarnings("unchecked")
    private void compareInternal(String currentPath, Object expected, Object actual, Set<String> ignorePaths,
            DiffResult result) {
        if (ignorePaths != null && ignorePaths.contains(currentPath)) {
            return;
        }

        if (expected == null && actual == null) return;
        if (expected == null || actual == null) {
            result.addDiff(currentPath, expected, actual);
            return;
        }

        if (expected instanceof Map && actual instanceof Map) {
            Map<String, Object> expMap = (Map<String, Object>) expected;
            Map<String, Object> actMap = (Map<String, Object>) actual;

            Set<String> allKeys = new HashSet<>(expMap.keySet());
            allKeys.addAll(actMap.keySet());

            for (String key : allKeys) {
                String subPath = currentPath.isEmpty() ? key : currentPath + "." + key;
                if (!expMap.containsKey(key)) {
                    result.addDiff(subPath, "<ABSENT>", actMap.get(key));
                } else if (!actMap.containsKey(key)) {
                    result.addDiff(subPath, expMap.get(key), "<ABSENT>");
                } else {
                    compareInternal(subPath, expMap.get(key), actMap.get(key), ignorePaths, result);
                }
            }
        } else if (expected instanceof List && actual instanceof List) {
            List<Object> expList = (List<Object>) expected;
            List<Object> actList = (List<Object>) actual;

            if (expList.size() != actList.size()) {
                result.addDiff(currentPath + ".length", expList.size(), actList.size());
            } else {
                for (int i = 0; i < expList.size(); i++) {
                    compareInternal(currentPath + "[" + i + "]", expList.get(i), actList.get(i), ignorePaths, result);
                }
            }
        } else {
            if (!expected.equals(actual)) {
                result.addDiff(currentPath, expected, actual);
            }
        }
    }

    public static void main(String[] args) {
        Solution engine = new Solution();

        // Build sample expected payload
        Map<String, Object> expected = new HashMap<>();
        expected.put("status", "ACTIVE");
        expected.put("timestamp", 1600000000L);
        Map<String, Object> user = new HashMap<>();
        user.put("name", "Alice");
        user.put("role", "ADMIN");
        expected.put("user", user);

        // Build sample actual payload with dynamic timestamp and role mismatch
        Map<String, Object> actual = new HashMap<>();
        actual.put("status", "ACTIVE");
        actual.put("timestamp", 1750000000L); // Dynamic field
        Map<String, Object> actUser = new HashMap<>();
        actUser.put("name", "Alice");
        actUser.put("role", "USER"); // Mismatch
        actual.put("user", actUser);

        // Test 1: Ignore timestamp, role should be caught
        Set<String> ignorePaths = new HashSet<>(Arrays.asList("timestamp"));
        DiffResult diff = engine.compare(expected, actual, ignorePaths);

        assert diff.hasDifferences() : "Test 1 Failed: Should detect difference in user.role";
        assert diff.differences.size() == 1 : "Test 1 Failed: Expected 1 diff, got " + diff.differences.size();
        assert diff.differences.get(0).contains("user.role") : "Test 1 Failed: Expected diff on user.role";

        // Test 2: Identical objects with no ignorePaths
        DiffResult diffIdentical = engine.compare(expected, expected, Collections.emptySet());
        assert !diffIdentical.hasDifferences() : "Test 2 Failed: Identical objects reported diffs";

        System.out.println("All 2 Java JSON Diff Engine test cases passed!");
    }
}
