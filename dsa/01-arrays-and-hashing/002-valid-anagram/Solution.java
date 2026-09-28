/**
 * Problem: Valid Anagram (LeetCode #242)
 * Pattern: Arrays & Hashing
 * Difficulty: Easy
 */
public class Solution {

    /**
     * Checks if string t is an anagram of string s.
     *
     * @param s Original string
     * @param t Target string
     * @return true if t is an anagram of s, false otherwise
     */
    public boolean isAnagram(String s, String t) {
        // TODO: Implement your solution here
        return false;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: Valid anagram
        assert sol.isAnagram("anagram", "nagaram") : "Test 1 Failed: Expected true";

        // Test 2: Invalid anagram
        assert !sol.isAnagram("rat", "car") : "Test 2 Failed: Expected false";

        // Test 3: Different lengths
        assert !sol.isAnagram("a", "ab") : "Test 3 Failed: Expected false";

        // Test 4: Single char identical
        assert sol.isAnagram("z", "z") : "Test 4 Failed: Expected true";

        System.out.println("All 4 Java test cases passed!");
    }
}
