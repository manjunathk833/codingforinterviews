/**
 * Problem: Valid Palindrome (LeetCode #125)
 * Pattern: Two Pointers
 * Difficulty: Easy
 */
public class Solution {

    /**
     * Determines whether a given string is a valid palindrome.
     *
     * @param s Input string
     * @return true if palindrome, false otherwise
     */
    public boolean isPalindrome(String s) {
        // TODO: Implement your solution here
        // Target: In-place two pointers, O(N) time, O(1) space
        int left = 0, right = s.length() - 1;

        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) {
                left++;
            }
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) {
                right--;
            }

            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) {
                return false;
            }
            left++;
            right--;
        }

        return true;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();

        // Test 1: Complex palindrome with punctuation
        assert sol.isPalindrome("A man, a plan, a canal: Panama") : "Test 1 Failed";

        // Test 2: Non-palindrome
        assert !sol.isPalindrome("race a car") : "Test 2 Failed";

        // Test 3: Whitespace only
        assert sol.isPalindrome(" ") : "Test 3 Failed";

        // Test 4: Alphanumeric with numbers
        assert sol.isPalindrome("0P") == false : "Test 4 Failed";

        System.out.println("All 4 Java test cases passed!");
    }
}
