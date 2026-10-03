import java.util.HashSet;
import java.util.Set;

/**
 * Problem: Longest Consecutive Sequence (LeetCode #128)
 * Pattern: Arrays & Hashing
 * Difficulty: Medium
 */
public class Solution {

    public int longestConsecutive(int[] nums) {
        // TODO: Implement your solution here
        return 0;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1
        assert sol.longestConsecutive(new int[] { 100, 4, 200, 1, 3, 2 }) == 4 : "Test 1 Failed";

        // Test 2
        assert sol.longestConsecutive(new int[] { 0, 3, 7, 2, 5, 8, 4, 6, 0, 1 }) == 9 : "Test 2 Failed";

        // Test 3: Empty array
        assert sol.longestConsecutive(new int[] {}) == 0 : "Test 3 Failed";

        // Test 4: Single element
        assert sol.longestConsecutive(new int[] { 10 }) == 1 : "Test 4 Failed";

        System.out.println("All 4 Java test cases passed!");
    }
}
