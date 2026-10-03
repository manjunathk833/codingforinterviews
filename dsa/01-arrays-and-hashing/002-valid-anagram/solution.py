"""Problem: Valid Anagram (LeetCode #242)
Pattern: Arrays & Hashing
Difficulty: Easy
"""


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # TODO: Implement your solution here
        return False


if __name__ == "__main__":
    sol = Solution()

    # Test 1
    assert sol.isAnagram("anagram", "nagaram") is True, "Test 1 Failed"

    # Test 2
    assert sol.isAnagram("rat", "car") is False, "Test 2 Failed"

    # Test 3
    assert sol.isAnagram("a", "ab") is False, "Test 3 Failed"

    # Test 4
    assert sol.isAnagram("z", "z") is True, "Test 4 Failed"

    print("All 4 Python test cases passed!")
