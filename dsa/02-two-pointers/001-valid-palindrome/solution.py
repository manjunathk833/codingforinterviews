"""Problem: Valid Palindrome (LeetCode #125)
Pattern: Two Pointers
Difficulty: Easy
"""


class Solution:
    def isPalindrome(self, s: str) -> bool:
        """Determines if s is a palindrome using O(1) auxiliary space.

        Time Complexity: O(N)
        Space Complexity: O(1)
        """
        left, right = 0, len(s) - 1

        while left < right:
            while left < right and not s[left].isalnum():
                left += 1
            while left < right and not s[right].isalnum():
                right -= 1

            if s[left].lower() != s[right].lower():
                return False
            left += 1
            right -= 1

        return True


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    assert sol.isPalindrome("A man, a plan, a canal: Panama") is True, "Test 1 Failed"

    # Test 2
    assert sol.isPalindrome("race a car") is False, "Test 2 Failed"

    # Test 3
    assert sol.isPalindrome(" ") is True, "Test 3 Failed"

    # Test 4
    assert sol.isPalindrome("0P") is False, "Test 4 Failed"

    print("All 4 Python test cases passed!")
