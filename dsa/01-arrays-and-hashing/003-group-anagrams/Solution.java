import java.util.*;

/**
 * Problem: Group Anagrams (LeetCode #49)
 * Pattern: Arrays & Hashing
 * Difficulty: Medium
 *
 * Time Complexity: O(M * N) where M is the number of strings, N is the maximum length of a string.
 * Space Complexity: O(M * N) to store the grouped anagram lists in the hash map.
 */
public class Solution {

    /**
     * Groups anagrams together from the input array of strings using character
     * frequency counting as the hash map key.
     *
     * @param strs Array of strings
     * @return List of groups of anagrams
     */
    public List<List<String>> groupAnagrams(String[] strs) {
        if (strs == null || strs.length == 0) {
            return new ArrayList<>();
        }

        Map<String, List<String>> map = new HashMap<>();

        for (String s : strs) {
            // Count frequencies of characters 'a' through 'z'
            int[] count = new int[26];
            for (int i = 0; i < s.length(); i++) {
                count[s.charAt(i) - 'a']++;
            }

            // Build unique key from frequency counts: e.g. "#1#0#0#...#1"
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 26; i++) {
                sb.append('#').append(count[i]);
            }
            String key = sb.toString();

            map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }

        return new ArrayList<>(map.values());
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: Multiple anagram groups
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

        // Test 4: All strings are anagrams of each other
        String[] input4 = { "abc", "bca", "cab", "cba" };
        List<List<String>> res4 = sol.groupAnagrams(input4);
        assert res4.size() == 1 && res4.get(0).size() == 4 : "Test 4 Failed";

        // Test 5: No anagrams present
        String[] input5 = { "a", "b", "c" };
        List<List<String>> res5 = sol.groupAnagrams(input5);
        assert res5.size() == 3 : "Test 5 Failed";

        // Test 6: Empty input array
        String[] input6 = {};
        List<List<String>> res6 = sol.groupAnagrams(input6);
        assert res6.isEmpty() : "Test 6 Failed: Expected empty result for empty input";

        System.out.println("All 6 Java test cases passed!");
    }
}
