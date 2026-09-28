import java.util.*;

/**
 * Problem: Group Anagrams (LeetCode #49)
 * Pattern: Arrays & Hashing
 * Difficulty: Medium
 */
public class Solution {

    /**
     * Groups anagrams together from the input array of strings.
     *
     * @param strs Array of strings
     * @return List of groups of anagrams
     */
    public List<List<String>> groupAnagrams(String[] strs) {
        // TODO: Implement your solution here
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: Multiple groups
        String[] input1 = { "eat", "tea", "tan", "ate", "nat", "bat" };
        List<List<String>> res1 = sol.groupAnagrams(input1);
        assert res1.size() == 3 : "Test 1 Failed: Expected 3 groups, got " + res1.size();

        // Test 2: Empty string
        String[] input2 = { "" };
        List<List<String>> res2 = sol.groupAnagrams(input2);
        assert res2.size() == 1 && res2.get(0).get(0).equals("") : "Test 2 Failed";

        // Test 3: Single char
        String[] input3 = { "a" };
        List<List<String>> res3 = sol.groupAnagrams(input3);
        assert res3.size() == 1 && res3.get(0).get(0).equals("a") : "Test 3 Failed";

        System.out.println("All 3 Java test cases passed!");
    }
}
