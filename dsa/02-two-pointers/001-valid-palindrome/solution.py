"""Problem: Valid Palindrome (LeetCode #125)
Pattern: Two Pointers
Difficulty: Easy
"""


class Solution:
    def isPalindrome(self, s: str) -> bool:
        # TODO: Implement your solution here
        return False


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
