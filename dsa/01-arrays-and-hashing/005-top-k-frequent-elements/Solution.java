import java.util.*;

public class Solution {

    public int[] topKFrequent(int[] nums, int k) {
        // Frequency map
        Map<Integer, Integer> count = new HashMap<>();
        for (int n : nums) {
            count.put(n, count.getOrDefault(n, 0) + 1);
        }

        // Bucket sort where index represents frequency
        List<Integer>[] bucket = new List[nums.length + 1];
        for (int key : count.keySet()) {
            int freq = count.get(key);
            if (bucket[freq] == null) {
                bucket[freq] = new ArrayList<>();
            }
            bucket[freq].add(key);
        }

        int[] res = new int[k];
        int idx = 0;
        for (int i = bucket.length - 1; i >= 0 && idx < k; i--) {
            if (bucket[i] != null) {
                for (int num : bucket[i]) {
                    res[idx++] = num;
                    if (idx == k) break;
                }
            }
        }
        return res;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        int[] res1 = sol.topKFrequent(new int[] { 1, 1, 1, 2, 2, 3 }, 2);
        Arrays.sort(res1);
        assert Arrays.equals(res1, new int[] { 1, 2 }) : "Test 1 Failed";

        int[] res2 = sol.topKFrequent(new int[] { 1 }, 1);
        assert Arrays.equals(res2, new int[] { 1 }) : "Test 2 Failed";

        System.out.println("All 2 Java test cases passed!");
    }
}
