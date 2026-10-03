import java.util.*;

public class Solution {

    public int[] topKFrequent(int[] nums, int k) {
        // TODO: Implement your solution here
        return new int[] {};
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
